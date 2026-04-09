# 🔍 Debugging & Troubleshooting

Telemetry flowing? Brain working? If not, this guide will help you find the source of the problem.

## 📁 1. Where are the Logs?
NeurOps centralizes all operational data in the `logs/` directory.

- `logs/neurosight.log`: Look here if telemetry isn't reaching the dashboard or Google Cloud.
- `logs/chaos.log`: Look here if chaos injections aren't working.
- `logs/neurotalk.log`: Look here if the AI Assistant is giving errors.

**Pro-Tip**: Use `tail -f logs/*.log` to watch the whole system heartbeat.

---

## 🛑 2. Common Failures

### `DefaultCredentialsError` (Google Cloud)
**Symptoms**: `Neurosight` or `NeuroTalk` crashes with a message about "Application Default Credentials".
**Fix**:
```bash
gcloud auth application-default login
```

### `Permission Denied` (Docker)
**Symptoms**: `make startneurops` hangs or fails while starting redfish containers.
**Fix**:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### `Port already in use` (8001, 8080, 8501, etc.)
**Symptoms**: A specific service fails to start while others work.
**Fix**:
Find and kill the process using the port:
```bash
sudo lsof -i :8501
kill -9 <PID>
```

---

### `LlmAgent object has no attribute 'run'`
**Symptoms**: The AI chat interface shows an error when you ask a question.
**What it means**: This usually happens if there is a mismatch in the Google ADK version.
**Status**: This is automatically fixed by the `helpers.py` shim. Ensure your codebase is up to date with the latest `Makefile` fixes.

---

## 🧩 3. Diagnostic Commands

### Ecosystem Status
`make status` is your first line of defense. It checks if the PIDs exist and if the processes are actually alive.

### Network Ping
Check if the simulator is alive manually:
```bash
curl http://localhost:8001/redfish/v1/Systems
```

### Pub/Sub Check
Check if messages are reaching Google Cloud:
1.  Go to the [GCP Console](https://console.cloud.google.com/cloudpubsub/topic/list).
2.  Select your topic.
3.  Go to the "Messages" tab and click "PULL".

---

> [!NOTE]
> If you find a new bug or a weird edge case, please contribute the fix to our [FAQ](12-faq.md).
