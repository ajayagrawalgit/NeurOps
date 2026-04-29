import requests
from google.cloud import bigquery
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers import load_configs

_CONFIG = load_configs()

# Stale config removed to favor dynamic loading in get_live_status()


def get_live_status() -> dict:
    """Fetch current health, CPU, memory, and temperature of all servers"""
    # Reload config to ensure we have the latest server list if config.yaml was updated
    config = load_configs()
    servers = config.get("SERVERS", [])
    proxy_base = config.get("PROXY_BASE")
    
    results = {}

    for server in servers:
        sid = server["id"]

        try:
            url = f"{proxy_base}/redfish/{sid}/v1/Systems"
            res = requests.get(url, timeout=3).json()

            # The proxy unwraps Members[0] for us, so res is the system object
            system = res

            # Add fallbacks for simulation clarity (consistent with neurosight.py)
            results[sid] = {
                "cpu": system.get("Processors", {}).get("UsagePercent", 10.0),
                "memory": system.get("Memory", {}).get("UsagePercent", 20.0),
                "temp": system.get("Thermal", {}).get("TemperatureCelsius", 41.0),
                "power": system.get("PowerState", "Off"),
                "health": system.get("Status", {}).get("Health", "OK"),
            }

        except Exception as e:
            results[sid] = {"error": str(e)}

    return results


def get_redfish_status(server_id: str) -> dict:
    """Fetch full Redfish system telemetry for a specific server_id"""
    config = load_configs()
    proxy_base = config.get("PROXY_BASE")
    
    try:
        url = f"{proxy_base}/redfish/{server_id}/v1/Systems"
        res = requests.get(url, timeout=3)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return {"error": f"Failed to fetch Redfish status for {server_id}: {str(e)}"}


def get_past_issues(device_id: str) -> list:
    """Fetch last 10 telemetry records for a given device from BigQuery"""
    config = load_configs()
    project_id = config.get("PROJECT_ID")
    bq_client = bigquery.Client(project=project_id)

    query = f"""
    SELECT timestamp, cpu_usage, memory_usage, temperature, health_status
    FROM `{project_id}.neurops.hardware_telemetry`
    WHERE device_id = '{device_id}'
    ORDER BY timestamp DESC
    LIMIT 10
    """

    rows = bq_client.query(query).result()
    return [dict(row) for row in rows]