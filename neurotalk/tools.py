import requests
from google.cloud import bigquery
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers import load_configs

_CONFIG = load_configs()

SERVERS = _CONFIG.get("SERVERS", [])
PROXY_BASE = _CONFIG.get("PROXY_BASE")

bq_client = bigquery.Client(project=_CONFIG.get("PROJECT_ID"))


def get_live_status() -> dict:
    """Fetch current health, CPU, memory, and temperature of all servers"""
    results = {}

    for server in SERVERS:
        sid = server["id"]

        try:
            url = f"{PROXY_BASE}/redfish/{sid}/v1/Systems"
            res = requests.get(url, timeout=3).json()

            system = res.get("Members", [{}])[0]

            results[sid] = {
                "cpu": system.get("Processors", {}).get("UsagePercent"),
                "memory": system.get("Memory", {}).get("UsagePercent"),
                "temp": system.get("Thermal", {}).get("TemperatureCelsius"),
                "power": system.get("PowerState"),
                "health": system.get("Status", {}).get("Health"),
            }

        except Exception as e:
            results[sid] = {"error": str(e)}

    return results


def get_past_issues(device_id: str) -> list:
    """Fetch last 10 telemetry records for a given device"""

    query = f"""
    SELECT timestamp, cpu_usage, memory_usage, temperature, health_status
    FROM `{_CONFIG["PROJECT_ID"]}.neurops.hardware_telemetry`
    WHERE device_id = '{device_id}'
    ORDER BY timestamp DESC
    LIMIT 10
    """

    rows = bq_client.query(query).result()
    return [dict(row) for row in rows]