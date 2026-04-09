# 📡 Module Breakdown: Telemetry & Anomaly Detection

**Neurosight** is the central nervous system of NeurOps. It is responsible for the observation, analysis, and ingestion of hardware health data.

## 📁 Key Files
- `neurosight/neurosight.py`: The core collection and analysis script.
- `helpers.py`: Handles Google Cloud ADC (Authentication).

---

## 🔍 1. The Collection Loop
Neurosight runs a continuous while-loop that performs the following steps every `POLL_INTERVAL` (default 10s):
1.  **Poll**: Requests JSON data from the **Chaos Proxy** for every server defined in `config.yaml`.
2.  **Extract**: Parses the complex Redfish JSON into a flat schema (`cpu_usage`, `memory_usage`, `temperature`).
3.  **Detect**: Runs anomaly detection (see below).
4.  **Batch**: Collects data from all servers into a single batch.
5.  **Publish**: Pushes the batch to **Google Cloud Pub/Sub**.

---

## 🚨 2. Anomaly Detection Logic
Neurosight doesn't just look at values; it looks at **behavior over time**.

### Threshold Alarms
Static checks based on the `THRESHOLDS` dictionary:
- **CPU > 90%**: `CPU_CRITICAL`
- **Temp > 85°C**: `TEMP_CRITICAL`

### Trend Detection (The "Magic" ✨)
Using a `deque` (Double-Ended Queue) with a window of 5 samples, Neurosight looks for patterns:
- **`is_increasing()`**: If the last 5 values for a metric are strictly increasing, it fires a `TREND_UP` alert (e.g., `TEMP_TREND_UP`).
- This allows us to catch a system that is gradually overheating *before* it hits a critical threshold.

---

## ☁️ 3. Google Cloud Integration
Neurosight is built to be "Cloud-Ready." 

- **Pub/Sub**: Enables real-time downstream consumers (Slack alerts, auto-scaling groups).
- **BigQuery**: By publishing batches to Pub/Sub, we enable an "Ingest-Once-Query-Many" pattern that eventually populates our BI tools and the AI Assistant's historical memory.

---

## ⚙️ Configuration
You can tune the sensitivity of the telemetry system in `config.yaml`:
- `POLL_INTERVAL`: How often to check (keep > 5s for simulator stability).
- `SERVERS`: Add or remove servers from the polling list.

---

> [!WARNING]
> **Authentication Required**: Neurosight will fail if it cannot find valid GCP credentials. Always run `gcloud auth application-default login` before starting.
