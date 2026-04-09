# ⚙️ Configuration Reference

NeurOps is designed to be highly configurable via a single YAML file and standard environment variables.

## 📄 config.yaml
This file is the "Source of Truth" for the ecosystem. It is located in the project root.

### Example Structure
```yaml
PROJECT_ID: "neur-ops-demo"
TOPIC_ID: "hardware-telemetry-v1"
POLL_INTERVAL: 10

SERVERS:
  - id: "server-1"
    url: "http://localhost:8001/redfish/v1/Systems"
  - id: "server-2"
    url: "http://localhost:8002/redfish/v1/Systems"

PROXY_BASE: "http://localhost:8080"
```

### Fields Explanation
- **`PROJECT_ID`**: The Google Cloud Project ID where your Pub/Sub and BigQuery resources live.
- **`TOPIC_ID`**: The name of the Pub/Sub topic where telemetry batches will be published.
- **`POLL_INTERVAL`**: (Seconds) How often `Neurosight` polls the servers. Lower values provide more "real-time" feel but consume more resources.
- **`SERVERS`**: A list of server objects. Each needs a unique `id` (slug) and the base `url` for its Redfish API.
- **`PROXY_BASE`**: The base URL of the Chaos Management Proxy.

---

## 🔐 Environment Variables
While YAML is used for system structure, Environment Variables are used for sensitive system-level configurations.

- **`GOOGLE_APPLICATION_CREDENTIALS`**: Path to your GCP Service Account JSON file. 
- **`PYTHONPATH`**: Automatically handled by the `Makefile` and `sys.path` logic in code.

---

## 🛠️ Dynamic Reloading
The **Chaos Proxy** and **NeuroTalk UI** support dynamic configuration reloading.

- **Chaos Proxy**: You can call the `/reload-config` endpoint to pick up new server list changes without restarting the FastAPI server.
- **NeuroTalk UI**: Streamlit will detect changes to `config.yaml` and offer to reload the user interface.

---

> [!TIP]
> **Production Override**: If you set an environment variable with the same name as a YAML key (e.g., `export PROJECT_ID=my-prod-project`), you should eventually update the code to prioritize the environment variable for better CI/CD compatibility.
