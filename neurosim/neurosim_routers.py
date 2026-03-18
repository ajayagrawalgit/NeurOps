import requests
from fastapi import FastAPI, HTTPException
import threading
import time
import sys
import os
from enum import Enum

# Ensure the parent directory is in sys.path so we can import helpers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers import load_configs

_CONFIG = load_configs()

app = FastAPI(title="NeurOps Redfish Chaos Proxy")

# 🔗 Load Servers from config
SERVERS = _CONFIG.get("SERVERS", [])
if not SERVERS:
    # Fallback if empty config
    SERVERS = [{"id": "server-1", "url": "http://localhost:8000/redfish/v1/Systems"}]

SERVER_MAP = {server["id"]: server["url"] for server in SERVERS}

# Auto-populate dropdown using Enum
# Enum("Name", {"KEY": "value"})
ServerEnum = Enum("ServerEnum", {s: s for s in SERVER_MAP.keys()})

# 🧠 Override layer (ONLY stores simulated changes, partitioning by server_id)
overrides = {s: {} for s in SERVER_MAP.keys()}

# -------------------------------
# 📡 Fetch Real Redfish Data
# -------------------------------
def get_real_redfish(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


# -------------------------------
# 🧬 Merge Overrides
# -------------------------------
def apply_overrides(server_id, data):
    if not isinstance(data, dict):
        return data
    
    server_overrides = overrides.get(server_id, {})
    
    if "Members" in data and isinstance(data["Members"], list):
        if len(data["Members"]) == 0:
            data["Members"].append({})
        system = data["Members"][0]
        for key, value in server_overrides.items():
            system[key] = value
    else:
        for key, value in server_overrides.items():
            data[key] = value
            
    return data


# -------------------------------
# 📡 Redfish Proxy Endpoint
# -------------------------------
@app.get("/redfish/{server_id}/v1/Systems")
def proxy_redfish(server_id: ServerEnum):
    url = SERVER_MAP.get(server_id.value)
    if not url:
        raise HTTPException(status_code=404, detail="Server not found")
        
    real_data = get_real_redfish(url)
    return apply_overrides(server_id.value, real_data)


# -------------------------------
# 🚨 Chaos APIs (Override Layer)
# -------------------------------

@app.post("/simulate/{server_id}/cpu/spike")
def cpu_spike(server_id: ServerEnum):
    overrides[server_id.value]["CPU"] = {
        "UsagePercent": 95,
        "Status": {"Health": "Critical"}
    }
    return {"message": f"CPU spike injected for {server_id.value}"}


@app.post("/simulate/{server_id}/disk/failure")
def disk_failure(server_id: ServerEnum):
    overrides[server_id.value]["Disk"] = {
        "Status": {"Health": "Critical", "State": "Failed"}
    }
    return {"message": f"Disk failure injected for {server_id.value}"}


@app.post("/simulate/{server_id}/memory/leak")
def memory_leak(server_id: ServerEnum):
    overrides[server_id.value]["Memory"] = {
        "UsagePercent": 92,
        "Status": {"Health": "Critical"}
    }
    return {"message": f"Memory leak injected for {server_id.value}"}


@app.post("/simulate/{server_id}/temperature/high")
def temp_high(server_id: ServerEnum):
    overrides[server_id.value]["Temperature"] = {
        "ReadingCelsius": 95,
        "Status": {"Health": "Critical"}
    }
    return {"message": f"High temperature injected for {server_id.value}"}


@app.post("/simulate/{server_id}/power/off")
def power_off(server_id: ServerEnum):
    overrides[server_id.value]["PowerState"] = "Off"
    return {"message": f"Power OFF simulated for {server_id.value}"}


@app.post("/simulate/{server_id}/reset")
def reset(server_id: ServerEnum):
    overrides[server_id.value].clear()
    return {"message": f"All simulations cleared for {server_id.value}"}


# -------------------------------
# 🧪 Gradual Degradation
# -------------------------------
def gradual_cpu(server_id_val):
    for i in range(50, 100, 5):
        overrides[server_id_val]["CPU"] = {
            "UsagePercent": i,
            "Status": {"Health": "Warning" if i < 90 else "Critical"}
        }
        time.sleep(2)

@app.post("/simulate/{server_id}/cpu/gradual")
def cpu_gradual(server_id: ServerEnum):
    threading.Thread(target=gradual_cpu, args=(server_id.value,)).start()
    return {"message": f"Gradual CPU degradation started for {server_id.value}"}