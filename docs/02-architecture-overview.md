# 🏗️ Architecture Overview

NeurOps is built on a distributed, event-driven architecture that separates hardware simulation, telemetry processing, and AI interaction.

## 🗺️ System Map

```mermaid
graph TD
    subgraph Simulation ["1. Simulation Layer"]
        Sim1[Redfish Sim 1]
        Sim2[Redfish Sim 2]
        Sim3[Redfish Sim 3]
        Proxy[Chaos Management Proxy]
    end

    subgraph Intelligence ["2. Intelligence Layer"]
        Sight[Neurosight Collector]
        PubSub[Google Pub/Sub]
        BQ[(BigQuery Warehouse)]
    end

    subgraph Interaction ["3. Interaction Layer"]
        ADK[NeuroTalk AI Agent]
        UI[Streamlit UI]
    end

    Sim1 & Sim2 & Sim3 --> Proxy
    Proxy --> Sight
    Sight --> PubSub
    PubSub -.-> BQ
    ADK -- Tools --> Sight
    ADK -. Tools .-> BQ
    UI -- Chat --> ADK
```

## 층 Layers Breakdown

### 1. Simulation Layer
- **Redfish Simulators**: Python-based emulators that speak the industry-standard DMTF Redfish protocol.
- **Chaos Management Proxy**: A FastAPI middle-layer that allows us to intercept and "poison" real-time telemetry to simulate failures like thermal runaway or memory leaks.

### 2. Intelligence Layer
- **Neurosight Collector**: The heartbeat of the system. It polls simulators, applies statistical anomaly detection, and batches data.
- **Google Cloud Data Stack**: Uses **Pub/Sub** for real-time messaging and **BigQuery** for long-term telemetry storage and trend analysis.

### 3. Interaction Layer
- **NeuroTalk (AI Agent)**: Powered by Google ADK and Gemini. It is "tool-aware," meaning it knows how to query both live status and historical data to answer complex natural language questions.
- **Streamlit Dashboard**: A high-visibility interface for monitoring server health and chatting with the assistant.

---

## 🛠️ Tech Stack

- **Linguistics**: Python 3.12 (standardized on `mylab` venv).
- **Frontend**: Streamlit.
- **APIs**: FastAPI / Uvicorn.
- **AI**: Google ADK / Gemini 3 Flash.
- **Infra**: Docker Compose.
- **Cloud**: Google Cloud (Pub/Sub, BigQuery).

---

> [!IMPORTANT]
> To understand how data moves through these layers in real-time, see the [Project Flow Guide](03-project-flow.md).
