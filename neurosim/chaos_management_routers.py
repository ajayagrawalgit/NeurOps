import requests
from fastapi import FastAPI, HTTPException
import threading
import time
import sys
import os
from enum import Enum
from typing import Dict, Any

# -------------------------------
# 🔧 Load Config
# -------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers import load_configs

_CONFIG = load_configs()

app = FastAPI(title="NeurOps Redfish Chaos Proxy")

# -------------------------------
# 🌐 Server Registry
# -------------------------------
def build_server_map(config):
    servers = config.get("SERVERS", [])
    return {s["id"]: s["url"] for s in servers}


SERVER_MAP: Dict[str, str] = build_server_map(_CONFIG)

if not SERVER_MAP:
    raise RuntimeError("No servers configured in config.yaml")

# Enum for Swagger dropdown
ServerEnum = Enum("ServerEnum", {s: s for s in SERVER_MAP.keys()})

# 🧠 Override layer (per server)
overrides: Dict[str, Dict[str, Any]] = {
    s: {} for s in SERVER_MAP.keys()
}


# -------------------------------
# 📡 Fetch Real Redfish Data
# -------------------------------
def get_real_redfish(url: str):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


# -------------------------------
# 🧬 Deep Merge (SAFE override)
# -------------------------------
def deep_merge(original: dict, override: dict):
    for key, value in override.items():
        if (
            key in original
            and isinstance(original[key], dict)
            and isinstance(value, dict)
        ):
            deep_merge(original[key], value)
        else:
            original[key] = value
    return original


def apply_overrides(server_id: str, data: dict):
    if not isinstance(data, dict):
        return data

    server_override = overrides.get(server_id, {})

    if "Members" in data and isinstance(data["Members"], list) and data["Members"]:
        system = data["Members"][0]
        return deep_merge(system, server_override)

    return deep_merge(data, server_override)


# -------------------------------
# 📡 Proxy Endpoints
# -------------------------------
@app.get("/")
def root():
    return {
        "message": "NeurOps Chaos Proxy Running 🚀",
        "servers": list(SERVER_MAP.keys()),
        "docs": "/docs"
    }


@app.get("/health")
def health():
    status = {}

    for server_id, url in SERVER_MAP.items():
        try:
            res = requests.get(url, timeout=2)
            status[server_id] = "UP" if res.status_code == 200 else "DOWN"
        except:
            status[server_id] = "DOWN"

    return status


@app.get("/redfish/{server_id}/v1/Systems")
def proxy_redfish(server_id: ServerEnum):
    url = SERVER_MAP.get(server_id.value)

    if not url:
        raise HTTPException(status_code=404, detail="Server not found")

    real_data = get_real_redfish(url)
    return apply_overrides(server_id.value, real_data)


@app.get("/redfish/v1/all-systems")
def get_all_systems():
    results = {}

    for server_id, url in SERVER_MAP.items():
        data = get_real_redfish(url)
        results[server_id] = apply_overrides(server_id, data)

    return results


# -------------------------------
# 🚨 Chaos APIs
# -------------------------------
@app.post("/simulate/{server_id}/cpu/spike")
def cpu_spike(server_id: ServerEnum):
    overrides[server_id.value]["Processors"] = {
        "UsagePercent": 95,
        "Status": {"Health": "Critical"}
    }
    return {"message": f"CPU spike injected for {server_id.value}"}


@app.post("/simulate/{server_id}/memory/leak")
def memory_leak(server_id: ServerEnum):
    overrides[server_id.value]["Memory"] = {
        "UsagePercent": 92,
        "Status": {"Health": "Critical"}
    }
    return {"message": f"Memory leak injected for {server_id.value}"}


@app.post("/simulate/{server_id}/disk/failure")
def disk_failure(server_id: ServerEnum):
    overrides[server_id.value]["Storage"] = {
        "Status": {"Health": "Critical", "State": "Failed"}
    }
    return {"message": f"Disk failure injected for {server_id.value}"}


@app.post("/simulate/{server_id}/temperature/high")
def temp_high(server_id: ServerEnum):
    overrides[server_id.value]["Thermal"] = {
        "TemperatureCelsius": 95,
        "Status": {"Health": "Critical"}
    }
    return {"message": f"High temperature injected for {server_id.value}"}


@app.post("/simulate/{server_id}/power/off")
def power_off(server_id: ServerEnum):
    overrides[server_id.value]["PowerState"] = "Off"
    return {"message": f"Power OFF simulated for {server_id.value}"}


@app.post("/simulate/{server_id}/power/on")
def power_on(server_id: ServerEnum):
    # Set PowerState to On. We can also just clear the override if we want base state, 
    # but explicitly setting 'On' is clearer.
    overrides[server_id.value]["PowerState"] = "On"
    return {"message": f"Power ON simulated for {server_id.value}"}


@app.post("/simulate/{server_id}/reset")
def reset(server_id: ServerEnum):
    overrides[server_id.value].clear()
    return {"message": f"Reset simulations for {server_id.value}"}


# -------------------------------
# 🧪 Gradual Degradation
# -------------------------------
def gradual_cpu(server_id_val: str):
    for i in range(50, 101, 5):
        overrides[server_id_val]["Processors"] = {
            "UsagePercent": i,
            "Status": {
                "Health": "Warning" if i < 90 else "Critical"
            }
        }
        time.sleep(2)


@app.post("/simulate/{server_id}/cpu/gradual")
def cpu_gradual(server_id: ServerEnum):
    threading.Thread(
        target=gradual_cpu,
        args=(server_id.value,),
        daemon=True
    ).start()

    return {"message": f"Gradual CPU degradation started for {server_id.value}"}


# -------------------------------
# 🔄 Reload Config (dynamic scaling)
# -------------------------------
@app.post("/reload-config")
def reload_config():
    global SERVER_MAP, overrides, ServerEnum

    new_config = load_configs()
    SERVER_MAP = build_server_map(new_config)

    if not SERVER_MAP:
        raise HTTPException(status_code=500, detail="No servers found")

    overrides = {s: {} for s in SERVER_MAP.keys()}
    ServerEnum = Enum("ServerEnum", {s: s for s in SERVER_MAP.keys()})

    return {
        "message": "Config reloaded successfully",
        "servers": list(SERVER_MAP.keys())
    }


# -------------------------------
# 🩹 Auto-Healing (Simulation Hooks)
# -------------------------------
@app.post("/heal/{server_id}/reboot")
def heal_reboot(server_id: ServerEnum):
    """
    Simulates a hardware reboot/power-cycle.
    In Production: This endpoint should trigger a real Redfish Reset or PDU cycle.
    """
    overrides[server_id.value].clear()
    return {"message": f"Power-cycle/Reboot triggered for {server_id.value}. System stabilized."}


@app.post("/heal/{server_id}/resource-recovery")
def heal_resources(server_id: ServerEnum):
    """
    Simulates clearing memory leaks or process spikes.
    In Production: This could trigger a service restart or container migration.
    """
    # Specifically clear resource-related overrides if they exist
    if "Processors" in overrides[server_id.value]:
        del overrides[server_id.value]["Processors"]
    if "Memory" in overrides[server_id.value]:
        del overrides[server_id.value]["Memory"]
    
    return {"message": f"Resource recovery automation executed for {server_id.value}."}