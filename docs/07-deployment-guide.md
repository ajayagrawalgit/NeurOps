# 🚀 Deployment Guide

While NeurOps is designed for local development and research, it is built to scale. This guide describes how to move the system from a single machine to a distributed environment.

## 🏛️ Deployment Architecture
In a production deployment, the layers are separated:

1.  **Edge**: Redfish Simulators (or real hardware) running in the data center.
2.  **Collection**: Neurosight instances running as sidecars or standalone services.
3.  **Ingestion**: Google Cloud Pub/Sub service.
4.  **Warehouse**: Google Cloud BigQuery.
5.  **Service**: NeuroTalk Backend (FastAPI) and UI (Streamlit) running on Cloud Run or GKE.

---

## ☁️ 1. Google Cloud Run (Recommended)
The **NeuroTalk Backend** and **Chaos Proxy** are perfect candidates for Google Cloud Run because they are stateless.

```bash
gcloud run deploy neurotalk --source .
```

### Environment Variables
Ensure you set the following in your Cloud Run configuration:
- `PROJECT_ID`: Your GCP Project.
- `TOPIC_ID`: The Pub/Sub topic for telemetry.
- `GOOGLE_APPLICATION_CREDENTIALS`: (Not needed in Cloud Run as it uses the Service Account identity).

---

## ☸️ 2. Kubernetes (GKE)
If you require high availability and complex networking, deploy the **Entire Stack** using K8s.

- **Simulators**: Deploy as a `StatefulSet` or multiple independent `Deployments`.
- **Neurosight**: Deploy as a `Deployment` with a single replica to avoid double-polling.
- **Chaos Proxy**: Deploy as a `Service` to act as the internal entry point.

---

## 🔒 3. Security Considerations
1.  **OIDC Authentication**: Wrap the Streamlit UI in **Google IAP (Identity-Aware Proxy)** to ensure only authorized users can chat with the assistant.
2.  **IAM Roles**: 
    - `Neurosight`: Needs `Pub/Sub Publisher` role.
    - `NeuroTalk`: Needs `BigQuery Data Viewer` and `Vertex AI User` roles.

---

## 📈 4. Scaling Simulators
The `config.yaml` based discovery allows you to scale up. You can have 1,000s of server entries. 

> [!CAUTION]
> If scaling beyond 10 servers, you should increase the `POLL_INTERVAL` in `neurosight.py` to avoid hitting API rate limits or overwhelming the Chaos Proxy.

---

> [!TIP]
> **Production vs. Development**: In production, delete the `neurosim/` directory and replace the `SERVERS` list in `config.yaml` with real Redfish URLs.
