import requests
import json
import time
import random
from datetime import datetime, timezone
from google.cloud import pubsub_v1

# ==============================
# CONFIG
# ==============================
PROJECT_ID = "bnb-apex"
TOPIC_ID = "telemetry-topic"

POLL_INTERVAL = 10  # seconds

# 🖥️ MULTIPLE SERVERS
SERVERS = [
    {"id": "server-1", "url": "http://localhost:8000/redfish/v1/Systems"}
    # {"id": "server-2", "url": "http://localhost:8001/redfish/v1/Systems"},
    # {"id": "server-3", "url": "http://localhost:8002/redfish/v1/Systems"},
]


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


# ==============================
# PARSE + PRINT
# ==============================
def parse_metrics(server_id, data):
    try:
        members = data.get("Members", [])
        system = members[0] if members else {}

        # Slight variation per server
        base = random.uniform(0, 1)

        cpu = round(40 + 30 * base, 2)
        memory = round(60 + 20 * base, 2)
        temp = round(65 + 20 * base, 2)

        power = system.get("PowerState", "On")

        metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "device_id": server_id,
            "cpu_usage": cpu,
            "memory_usage": memory,
            "temperature": temp,
            "power_state": power,
            "health_status": "OK",
            "raw_json": json.dumps(data)
        }

        # 🔥 TERMINAL OUTPUT
        print("\n" + "=" * 60)
        print(f"🖥️  Device        : {server_id}")
        print(f"⚡ CPU Usage      : {cpu}%")
        print(f"🧠 Memory Usage   : {memory}%")
        print(f"🌡️  Temperature   : {temp}°C")
        print(f"🔌 Power State    : {power}")
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
            data = fetch_redfish_data(server["url"])

            if data:
                metrics = parse_metrics(server["id"], data)

                if metrics:
                    publish(metrics)

        time.sleep(POLL_INTERVAL)


# ==============================
# ENTRYPOINT
# ==============================
if __name__ == "__main__":
    run()