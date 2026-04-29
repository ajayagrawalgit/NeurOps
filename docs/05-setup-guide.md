# 🛠️ Setup Guide: From Zero to NeurOps

Ready to launch? Follow these steps to get the entire NeurOps ecosystem running on your machine.

## 📋 Prerequisites
Ensure you have the following installed:
- **Python 3.12+**
- **Docker & Docker Compose**
- **Google Cloud SDK (gcloud)**
- **Make** (standard on Linux/macOS)

---

## 🏗️ Step 1: Environment Setup
Standardize your environment to avoid "it works on my machine" issues.

```bash
# We recommend labeling your venv 'mylab'
python3 -m venv mylab
source mylab/bin/activate
pip install -r requirements.txt
```

```bash
gcloud auth application-default login
```
This command will open a browser and generate a JSON credential file on your system.

## ☁️ Step 3: Google Cloud Project Setup
NeurOps requires a Google Cloud Project with Pub/Sub and BigQuery enabled.

1.  **Create a Project**: Go to the [GCP Console](https://console.cloud.google.com/) and create a project (e.g., `neur-ops-demo`).
2.  **Enable APIs**: Enable the **BigQuery API** and **Pub/Sub API**.
3.  **Create Pub/Sub Topic**: Create a topic named `telemetry-topic`.
4.  **Create BigQuery Dataset**:
    - Create a dataset named `neurops`.
5.  **Create BigQuery Table**:
    - Create a table named `hardware_telemetry` inside the `neurops` dataset.
    - **Schema**:
        | Field Name | Type | Mode |
        | :--- | :--- | :--- |
        | `timestamp` | TIMESTAMP | REQUIRED |
        | `device_id` | STRING | REQUIRED |
        | `cpu_usage` | FLOAT | NULLABLE |
        | `memory_usage` | FLOAT | NULLABLE |
        | `temperature` | FLOAT | NULLABLE |
        | `power_state` | STRING | NULLABLE |
        | `health_status` | STRING | NULLABLE |
        | `raw_json` | STRING | NULLABLE |

## ⚙️ Step 4: Local Configuration
Before running, you must point the project to your specific GCP resources.

1.  Open [**config.yaml**](../config.yaml) in the root directory.
2.  Update the following fields:
    - `PROJECT_ID`: Your exact Google Cloud Project ID.
    - `TOPIC_ID`: The name of your Pub/Sub topic (e.g., `telemetry-topic`).
3.  (Optional) Adjust the `POLL_INTERVAL` or add more simulated servers to the `SERVERS` list.

---

### 🏭 Transitioning to Production
NeurOps is designed to be **Production-First**. Once you have validated your workflows using the built-in emulators, you can transition to real hardware in minutes:

1.  **Skip Emulation**: You do not need to run `make startneurosim` or the Docker containers in production.
2.  **Update Endpoints**: In `config.yaml`, replace the `localhost` URLs in the `SERVERS` list with the HTTPS URLs of your actual server BMCs (e.g., `https://10.0.5.21/redfish/v1/Systems`).
3.  **Authentication**: Ensure the **Neurosight Collector** has network visibility and appropriate Redfish credentials for the target hardware.
4.  **Scaling**: The architecture is stateless and horizontally scalable; you can deploy multiple collectors to handle thousands of servers.

---

### ⌨️ Alternative: One-Line CLI Setup
If you prefer the terminal, run these commands to configure your GCP infrastructure in seconds:

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# 1. Enable Required Services
gcloud services enable pubsub.googleapis.com bigquery.googleapis.com \
    storage.googleapis.com aiplatform.googleapis.com

# 2. Create Pub/Sub Topic
gcloud pubsub topics create telemetry-topic

# 3. Create BigQuery Dataset
bq mk --dataset --location=US neurops

# 4. Create BigQuery Table with Schema
bq mk --table \
  --description "Hardware telemetry data" \
  $PROJECT_ID:neurops.hardware_telemetry \
  timestamp:TIMESTAMP,device_id:STRING,cpu_usage:FLOAT,memory_usage:FLOAT,temperature:FLOAT,power_state:STRING,health_status:STRING,raw_json:STRING
```

---

## 🐳 Step 5: Docker Permissions (Linux Users)
If you see "Permission Denied" when running docker:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

## 🚀 Step 6: The "Big Green Button"
NeurOps is orchestrated via a powerful Makefile. To start everything (Simulators, Proxy, Sight, and UI) in one go:

```bash
make startneurops
```

> [!TIP]
> If you prefer to run services individually without using `make`, check out our [Manual Service Management Guide](13-manual-service-management.md)! 🛠️

### What happens next?
- You will see a waterfall of "Starting..." messages.
- A **Status Report** will appear with PIDs for all services.
- All logs will be piped into the `/logs` directory.

## 🧠 Step 7: Access the AI
Once the startup report shows that **NeuroTalk UI** is `RUNNING`, open your browser:
- **URL**: `http://localhost:8501`

---

## 🔍 Verification Checklist
- [ ] Run `make status` and ensure all rows are green.
- [ ] Check `logs/neurosight.log` for successful telemetry batches.
- [ ] In the UI, ask: *"Hello, what is the status of server-1?"*

---

> [!WARNING]
> If `make startneurops` fails, check the [Troubleshooting Guide](10-debugging-troubleshooting.md). Usually, it is either a missing GCP authentication or an occupied network port.
