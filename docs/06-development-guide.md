# 🛠️ Development Guide

Welcome, contributor! This guide explains how to extend and modify the NeurOps ecosystem safely.

## 🏗️ Project Layout
```text
NeurOps/
├── neurosim/     # Simulators & Chaos Logic (Module 1)
├── neurosight/   # Intelligence & Ingestion (Module 2)
├── neurotalk/    # AI Assistant & UI (Module 3)
├── logs/         # Centralized log repository
└── helpers.py    # Common utilities
```

---

## 🔧 1. Modifying the Simulator
If you want to add new telemetry types (e.g., Disk Health, Network Droprate):
1.  **Sushy-emulator**: Modify the mock data generator in `neurosim/`.
2.  **Chaos Proxy**: Update `chaos_management_routers.py` to handle the new field in its overrides.
3.  **Neurosight**: Update `neurosight.py` to extract and publish the new metric.

---

## 🧪 2. Creating Chaos Scenarios
Chaos scenarios are the best way to test the system's resilience.
- To add a new scenario, create an endpoint in `chaos_management_routers.py`.
- Example: `simulate/{server_id}/fan/failure`.
- Reset state in the `reset()` endpoint to ensure clean testing.

---

## 🧠 3. Improving the AI Agent
The Agent is only as good as its tools and instructions.

### System Instructions
If the agent is being too technical or not technical enough, adjust the `instruction` string in `neurotalk/agent.py`.

### Tool Development
New tools allow the agent to perform new actions (e.g., "reboot a server" or "query cost data").
- Place new tools in `neurotalk/tools.py`.
- Use Pydantic type hints for arguments.
- Always include a `docstring` that explains **why** and **when** the agent should use the tool.

---

## 📜 4. Coding Conventions
- **Asynchronous where possible**: Use `async`/`await` for I/O operations (APIs/Databases).
- **Graceful Failure**: Use try/except blocks with clear logging so the whole system doesn't crash if one simulator is offline.
- **Config-Driven**: Never hardcode URLs or IDs. Add them to `config.yaml` and use `helpers.load_configs()`.

---

## 🧪 5. Testing your changes
1.  Run `make startneurops`.
2.  Trigger your change (e.g., call a new chaos API).
3.  Watch `logs/` to see how the system reacts.
4.  Confirm the UI correctly reflects the state.

---

> [!TIP]
> **Hot Reloading**: Streamlit supports auto-reload. When you save `neurotalk/neurotalk_app.py`, the UI will automatically prompt you to refresh.
