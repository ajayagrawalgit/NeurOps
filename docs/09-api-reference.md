# 📖 API Reference

NeurOps exposes several APIs to manage hardware simulation, inject chaos, and interact with the AI assistant.

---

## 🌀 Chaos Management Proxy
**Base URL**: `http://localhost:8080` (Default)  
**Interactive Docs**: `http://localhost:8080/docs` (Swagger UI)

### 🚨 Chaos Injection Endpoints

#### `POST /simulate/{server_id}/cpu/spike`
- **Description**: Forces the CPU usage of the specified server to 95%.
- **Response**: `{"message": "CPU spike injected for server-1"}`

#### `POST /simulate/{server_id}/temperature/high`
- **Description**: Forces the temperature reading to 95°C.
- **Response**: `{"message": "High temperature injected for server-1"}`

#### `POST /simulate/{server_id}/disk/failure`
- **Description**: Sets the storage status to `Failed` and Health to `Critical`.

#### `POST /simulate/{server_id}/reset`
- **Description**: Clears all active simulations for the target server and returns it to its base state.

### 🩹 Auto-Healing (Automation Hooks)
These endpoints serve as standardized integration points for production remediation workflows. While they simulate recovery in this environment, they are designed to be tied to actual workload automation.

#### `POST /heal/{server_id}/reboot`
- **Description**: Simulates a hardware power-cycle or system reboot.
- **Production Note**: Can be tied to real Redfish Reset commands or Intelligent PDU cycles.

#### `POST /heal/{server_id}/resource-recovery`
- **Description**: Simulates clearing resource spikes or memory leaks.
- **Production Note**: Use this as a hook for automation that restarts services or migrates workloads.

---

## 🧠 NeuroTalk Backend
**Base URL**: `http://localhost:8000` (Default)

#### `POST /ask`
- **Description**: Send a natural language question to the AI Agent.
- **Request Body**:
  ```json
  {
    "question": "Show me the health status of all servers."
  }
  ```
- **Response**:
  ```json
  {
    "answer": "All servers are currently healthy except server-1, which is reporting high temperatures."
  }
  ```

---

## 📡 Redfish Simulators
**Base URL**: `http://localhost:8001` (to 8003)

#### `GET /redfish/v1/Systems`
- **Description**: Standard Redfish collection endpoint.
- **Note**: These should usually be accessed via the Chaos Proxy for the best experience.

---

> [!TIP]
> **Swagger/OpenAPI**: Since we use FastAPI, you can always visit `/docs` on any API port to see the full, interactive documentation and try out endpoints directly from your browser.
