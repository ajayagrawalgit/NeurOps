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

## ☁️ Step 2: Google Cloud Authentication
NeurOps uses BigQuery, Pub/Sub, and Gemini. You must authenticate your local machine.

```bash
gcloud auth application-default login
```
This command will open a browser and generate a JSON credential file on your system.

## 🐳 Step 3: Docker Permissions (Linux Users)
If you see "Permission Denied" when running docker:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

## 🚀 Step 4: The "Big Green Button"
NeurOps is orchestrated via a powerful Makefile. To start everything (Simulators, Proxy, Sight, and UI) in one go:

```bash
make startneurops
```

### What happens next?
- You will see a waterfall of "Starting..." messages.
- A **Status Report** will appear with PIDs for all services.
- All logs will be piped into the `/logs` directory.

## 🧠 Step 5: Access the AI
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
