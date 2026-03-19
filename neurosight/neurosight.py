import requests
import json
import time
import sys
import os
from datetime import datetime, timezone
from urllib.parse import urlparse
from collections import deque
from typing import Dict, Any, List
from google.cloud import pubsub_v1

# -------------------------------
# 🔧 Load Config
# -------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers import load_configs

_CONFIG = load_configs()

PROJECT_ID = _CONFIG.get("PROJECT_ID")
TOPIC_ID = _CONFIG.get("TOPIC_ID")
POLL_INTERVAL = _CONFIG.get("POLL_INTERVAL", 10)

SERVERS = _CONFIG.get("SERVERS", [])
USE_PROXY = _CONFIG.get("USE_PROXY", True)
PROXY_BASE = _CONFIG.get("PROXY_BASE")

# -------------------------------
# ⚙️ Thresholds (can move to config later)
# -------------------------------
THRESHOLDS = {
    "cpu_critical": 90,
    "cpu_warning": 75,
    "memory_critical": 90,
    "memory_warning": 75,
    "temp_critical": 85,
    "temp_warning": 70,
}

TREND_WINDOW = 5  # last N samples

# -------------------------------
# 📡 PubSub Setup
# -------------------------------
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

# -------------------------------
# 🧠 State Store (for trends)
# -------------------------------
STATE: Dict[str, Dict[str, deque]] = {}

def init_state(server_id):
    if server_id not in STATE:
        STATE[server_id] = {
            "cpu": deque(maxlen=TREND_WINDOW),
            "memory": deque(maxlen=TREND_WINDOW),
            "temp": deque(maxlen=TREND_WINDOW),
        }

# -------------------------------
# 🔁 Retry Wrapper
# -------------------------------
def fetch_with_retry(url, retries=3, backoff=2):
    for attempt in range(retries):
        try:
            res = requests.get(url, timeout=5)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            if attempt == retries - 1:
                print(f"[ERROR] {url} failed after {retries} retries: {e}")
                return None
            time.sleep(backoff ** attempt)

# -------------------------------
# 🔗 Fetch Redfish System
# -------------------------------
def fetch_system_data(server_url):
    collection = fetch_with_retry(server_url) or {}
    members = collection.get("Members", [])
    if members:
        sys_uri = members[0].get("@odata.id")
        if sys_uri:
            p = urlparse(server_url)
            base = f"{p.scheme}://{p.netloc}"
            system_data = fetch_with_retry(f"{base}{sys_uri}") or {}
            # Fetch Chassis Thermal data to use as a fallback when Chaos Proxy isn't overriding
            chassis_links = system_data.get("Links", {}).get("Chassis", [])
            if chassis_links:
                chassis_uri = chassis_links[0].get("@odata.id")
                if chassis_uri:
                    thermal_data = fetch_with_retry(f"{base}{chassis_uri}/Thermal") or {}
                    if "Temperatures" in thermal_data and len(thermal_data["Temperatures"]) > 0:
                        system_data["_RealTemperature"] = thermal_data["Temperatures"][0].get("ReadingCelsius")
            return system_data
    return collection

# -------------------------------
# 🧬 Merge Chaos + Real
# -------------------------------
def deep_merge(original, override):
    for k, v in override.items():
        if k in original and isinstance(original[k], dict) and isinstance(v, dict):
            deep_merge(original[k], v)
        else:
            original[k] = v
    return original

def apply_proxy(server_id, real_data):
    if not USE_PROXY:
        return real_data
    proxy_url = f"{PROXY_BASE}/redfish/{server_id}/v1/Systems"
    chaos = fetch_with_retry(proxy_url) or {}
    chaos_system = (
        chaos.get("Members", [{}])[0]
        if "Members" in chaos else chaos
    )
    return deep_merge(real_data, chaos_system)

# -------------------------------
# 📊 Extract Metrics
# -------------------------------
def extract_metrics(server_id, data):
    try:
        # Fallback to defaults since Sushy Emulator doesn't natively expose Processors/Memory metrics
        cpu = data.get("Processors", {}).get("UsagePercent", 10.0)
        memory = data.get("Memory", {}).get("UsagePercent", 20.0)
        # Use Chaos proxy data first, then real Chassis data, then default
        temp = data.get("Thermal", {}).get("TemperatureCelsius", 
                                           data.get("_RealTemperature", 30.0))
        power = data.get("PowerState", "Unknown")
        health = data.get("Status", {}).get("Health", "OK")
        disk_state = data.get("Storage", {}).get("Status", {}).get("State", "OK")
        if disk_state == "Failed":
            health = "Critical"
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "device_id": server_id,
            "cpu_usage": cpu,
            "memory_usage": memory,
            "temperature": temp,
            "power_state": power,
            "health_status": health,
            "raw_json": json.dumps(data),
        }
    except Exception as e:
        print(f"[WARN] Failed extracting metrics for {server_id}: {e}")
        return None

# -------------------------------
# 🚨 Anomaly Detection
# -------------------------------
def detect_anomaly(server_id, metrics):
    init_state(server_id)
    cpu = metrics["cpu_usage"]
    memory = metrics["memory_usage"]
    temp = metrics["temperature"]
    STATE[server_id]["cpu"].append(cpu)
    STATE[server_id]["memory"].append(memory)
    STATE[server_id]["temp"].append(temp)
    alerts = []
    # Threshold checks
    if cpu >= THRESHOLDS["cpu_critical"]:
        alerts.append("CPU_CRITICAL")
    elif cpu >= THRESHOLDS["cpu_warning"]:
        alerts.append("CPU_WARNING")
    if memory >= THRESHOLDS["memory_critical"]:
        alerts.append("MEMORY_CRITICAL")
    if temp >= THRESHOLDS["temp_critical"]:
        alerts.append("TEMP_CRITICAL")

    # Trend detection (increasing pattern)
    def is_increasing(arr):
        return len(arr) == TREND_WINDOW and all(x < y for x, y in zip(arr, list(arr)[1:]))
    if is_increasing(STATE[server_id]["cpu"]):
        alerts.append("CPU_TREND_UP")
    if is_increasing(STATE[server_id]["temp"]):
        alerts.append("TEMP_TREND_UP")
    return alerts

# -------------------------------
# 📤 Batch Publish
# -------------------------------
def publish_batch(messages: List[Dict]):
    futures = []
    for m in messages:
        futures.append(
            publisher.publish(
                topic_path,
                json.dumps(m).encode("utf-8")
            )
        )

    for f in futures:
        try:
            f.result()
        except Exception as e:
            print(f"[ERROR] Publish failed: {e}")

# -------------------------------
# 🧠 Pretty Logging
# -------------------------------
def log_metrics(metrics, alerts):
    print("\n" + "=" * 60)
    print(f"🖥️  {metrics['device_id']}")
    print(f"CPU      : {metrics['cpu_usage']}%")
    print(f"Memory   : {metrics['memory_usage']}%")
    print(f"Temp     : {metrics['temperature']}°C")
    print(f"Power    : {metrics['power_state']}")
    print(f"Health   : {metrics['health_status']}")
    print(f"Alerts   : {alerts if alerts else 'None'}")
    print("=" * 60)

# -------------------------------
# 🔁 Main Loop
# -------------------------------
def run():
    print("🚀 NeurOps Neurosight v2 Starting...")
    print(f"☁️ PubSub: {topic_path}")
    print(f"🖥️ Servers: {len(SERVERS)}")
    print("=" * 60)
    while True:
        batch = []
        for server in SERVERS:
            server_id = server["id"]
            url = server["url"]
            real_data = fetch_system_data(url)
            if not real_data:
                continue
            merged = apply_proxy(server_id, real_data)
            metrics = extract_metrics(server_id, merged)
            if not metrics:
                continue
            alerts = detect_anomaly(server_id, metrics)
            metrics["alerts"] = alerts
            log_metrics(metrics, alerts)
            batch.append(metrics)
        if batch:
            publish_batch(batch)
        time.sleep(POLL_INTERVAL)

# -------------------------------
# 🚪 Entry
# -------------------------------
if __name__ == "__main__":
    run()