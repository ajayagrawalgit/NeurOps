# 🕹️ Module Breakdown: Infrastructure & Chaos Interface

The **Infrastructure & Chaos Layer** is the gateway between NeurOps and the physical hardware. It is designed to be protocol-compliant, ensuring that NeurOps can manage both emulated environments and real-world production servers with identical logic.

## 📁 Key Files
- `neurosim/chaos_management_routers.py`: The production-grade Chaos Proxy (includes Auto-Healing hooks).
- `neurosim/docker-compose.yml`: Orchestrates the validation environment (simulators).
- `neurosim/Dockerfile`: Blueprint for the scaled endpoint emulators.

---

## 🏗️ 1. Redfish Connectivity
NeurOps communicates with hardware using the **DMTF Redfish** standard.
- **In Development/Testing**: We use emulated endpoints based on `sushy-tools` to provide a safe sandbox for AI training and chaos testing.
- **In Production**: We target real BMC (Baseboard Management Controller) IP addresses. Because NeurOps is protocol-standardized, the **Neurosight Collector** and **NeuroTalk AI** behave identically in both scenarios.

---

## 🩹 2. Auto-Healing Hooks
The Chaos Proxy includes standardized endpoints for **Auto-Healing** (reboots, resource recovery).
- **Simulated Recovery**: In the validation environment, these endpoints clear active overrides to "stabilize" the emulated hardware.
- **Production Integration**: These endpoints are designed as **standardized API hooks**. Field engineers can easily tie these endpoints to real-world automation logic (e.g., Redfish Reset commands, Ansible playbooks, or Kubernetes remediation controllers) to enable full, autonomous self-healing in production.

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
