import requests
import json
import time
import random
import sys
import os
from datetime import datetime, timezone
from urllib.parse import urlparse
from google.cloud import pubsub_v1

# Ensure the parent directory is in sys.path so we can import helpers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers import load_configs

_CONFIG = load_configs()
PROJECT_ID = _CONFIG.get("PROJECT_ID", "bnb-apex")
TOPIC_ID = _CONFIG.get("TOPIC_ID", "telemetry-topic")

POLL_INTERVAL = _CONFIG.get("POLL_INTERVAL", 10)  # seconds

# 🖥️ MULTIPLE SERVERS
SERVERS = _CONFIG.get("SERVERS", [
    {"id": "server-1", "url": "http://localhost:8000/redfish/v1/Systems"}
])

USE_PROXY = _CONFIG.get("USE_PROXY", True)
PROXY_BASE = _CONFIG.get("PROXY_BASE", "http://localhost:8080")

# ==============================
# PUBSUB SETUP
# ==============================
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)


# ==============================
# FETCH DATA
# ==============================
def fetch_redfish_data(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[ERROR] Failed to fetch from {url}: {e}")
        return None

def deep_merge(original, override):
    for key, value in override.items():
        if key in original and isinstance(original[key], dict) and isinstance(value, dict):
            deep_merge(original[key], value)
        else:
            original[key] = value
    return original

# ==============================
# PARSE + PRINT
# ==============================
def parse_metrics(server_id, system_data):
    try:
        # Slight variation per server default
        base = random.uniform(0, 1)

        # Retrieve exact keys updated by chaos APIs
        cpu = system_data.get("Processors", {}).get("UsagePercent", round(40 + 30 * base, 2))
        memory = system_data.get("Memory", {}).get("UsagePercent", round(60 + 20 * base, 2))
        temp = system_data.get("Thermal", {}).get("TemperatureCelsius", round(65 + 20 * base, 2))
        power = system_data.get("PowerState", "On")
        health = system_data.get("Status", {}).get("Health", "OK")
        
        # Additional chaos key check
        disk_status = system_data.get("Storage", {}).get("Status", {}).get("State", "OK")
        if disk_status == "Failed":
             health = "Critical"

        metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "device_id": server_id,
            "cpu_usage": cpu,
            "memory_usage": memory,
            "temperature": temp,
            "power_state": power,
            "health_status": health,
            "raw_json": json.dumps(system_data)
        }

        # 🔥 TERMINAL OUTPUT
        print("\n" + "=" * 60)
        print(f"🖥️  Device        : {server_id}")
        print(f"⚡ CPU Usage      : {cpu}%")
        print(f"🧠 Memory Usage   : {memory}%")
        print(f"🌡️  Temperature   : {temp}°C")
        print(f"🔌 Power State    : {power}")
        print(f"🩺 Health Status  : {health}")
        print(f"🕒 Timestamp      : {metrics['timestamp']}")
        print("=" * 60)

        return metrics

    except Exception as e:
        print(f"[ERROR] Failed to parse metrics for {server_id}: {e}")
        return None


# ==============================
# PUBLISH
# ==============================
def publish(metrics):
    try:
        future = publisher.publish(
            topic_path,
            json.dumps(metrics).encode("utf-8")
        )
        message_id = future.result()
        print(f"📤 Published ({metrics['device_id']}): {message_id}")
    except Exception as e:
        print(f"[ERROR] Publish failed: {e}")


# ==============================
# MAIN LOOP
# ==============================
def run():
    print("🚀 Starting NeurOps Multi-Server Collector...")
    print(f"☁️ Publishing to: {topic_path}")
    print(f"🖥️ Monitoring {len(SERVERS)} servers")
    print("=" * 60)

    while True:
        for server in SERVERS:
            server_id = server["id"]
            server_url = server["url"]  # Real native server URL

            # 1. Fetch Real Redfish Collection
            real_collection = fetch_redfish_data(server_url) or {}
            members = real_collection.get("Members", [])
            
            system_data = real_collection
            if members:
                # 2. Traverse the endpoints
                sys_uri = members[0].get("@odata.id")
                if sys_uri:
                    p = urlparse(server_url)
                    real_host = f"{p.scheme}://{p.netloc}"
                    system_data = fetch_redfish_data(f"{real_host}{sys_uri}") or {}

            # 3. Pull from Chaos Proxy
            if USE_PROXY:
                proxy_url = f"{PROXY_BASE}/redfish/{server_id}/v1/Systems"
                chaos_data = fetch_redfish_data(proxy_url) or {}
                
                # neurosim_routers.py applies overrides directly to system dict (if it was a list)
                chaos_system = chaos_data.get("Members", [{}])[0] if "Members" in chaos_data else chaos_data
                
                # Merge chaos onto real data
                system_data = deep_merge(system_data, chaos_system)

            if system_data:
                metrics = parse_metrics(server_id, system_data)
                if metrics:
                    publish(metrics)

        time.sleep(POLL_INTERVAL)


# ==============================
# ENTRYPOINT
# ==============================
if __name__ == "__main__":
    run()