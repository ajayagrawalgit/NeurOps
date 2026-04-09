# 🎮 Module Breakdown: Simulation & Chaos

The **Simulation Layer** is where the NeurOps universe begins. It allows us to play "What if?" with our hardware without needing a real data center.

## 📁 Key Files
- `neurosim/docker-compose.yml`: Orchestrates the simulators.
- `neurosim/chaos_management_routers.py`: The "Chaos Proxy" API.
- `neurosim/Dockerfile`: Blueprint for the simulator containers.

---

## 🏗️ 1. Redfish Simulators
The simulators are based on the **Sushy-Emulator**. They mimic real Dell/HPE server responses.
- **Protocol**: Redfish (RESTful API).
- **Default Port Map**:
    - `redfish-1`: localhost:8001
    - `redfish-2`: localhost:8002
    - `redfish-3`: localhost:8003

### Gotcha: Persistence
The simulators use volumes mapped to `./neurosim/emulator-data`. If you want to reset a simulator's internal state completely, you must clear these directories or run `make stopneuriosim`.

---

## 🌀 2. Chaos Management Proxy
This is a FastAPI application that acts as an intelligent middleware. Instead of fetching data from simulators directly, we fetch it through this proxy.

### Why use a proxy?
In a real data center, pushing a server to 90°C is dangerous and slow. The Proxy allows us to:
1.  **Instant Simulation**: Inject a "critical" state into the JSON response instantly.
2.  **Gradual Failure**: Simulate a slowly dying fan or a gradual memory leak.
3.  **Isolation**: Test if our AI can detect anomalies without actually crashing our test environment.

### Important Functions
- `apply_overrides()`: Merges real simulator data with your active "chaos" settings.
- `cpu_gradual()`: A background thread that slowly increases CPU usage over several minutes.

---

## 🛠️ How to connect
If you are writing a new tool that needs hardware data, **always point to the Chaos Proxy (Port 8080)**, not the simulators directly.

Example Proxy URL:
`http://localhost:8080/redfish/server-1/v1/Systems`

---

> [!TIP]
> Want to see the full list of Chaos APIs? Check the [API Reference](../09-api-reference.md).
