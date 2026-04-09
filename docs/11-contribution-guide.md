# 🤝 Contribution Guide

We love contributions! Whether you're fixing a typo, adding a new chaos scenario, or training a smarter agent, here is how you can help.

---

## 🏗️ 1. Project Organization
NeurOps is organized by **Domain**:
- **Simulation**: Everything related to the Redfish world (`neurosim/`).
- **Intelligence**: Telemetry, Analysis, and Cloud Ingestion (`neurosight/`).
- **Interaction**: The AI Assistant and the UI (`neurotalk/`).

Try to keep your changes within these boundaries. If you need to share logic between domains, put it in `helpers.py`.

---

## 🛠️ 2. Development Workflow
1.  **Fork & Clone**: Get the code locally.
2.  **Venv**: Always use a virtual environment (`python3 -m venv mylab`).
3.  **Branch**: Create a feature branch (`git checkout -b feat/my-new-feature`).
4.  **Develop**: Write your code.
5.  **Test**: Verified using `make startneurops`.
6.  **Docs**: If you add an API or a feature, update the relevant file in `/docs`.

---

## 📜 3. Coding Standards
- **DRY (Don't Repeat Yourself)**: Use utility functions in BigQuery or Redfish logic.
- **Type Hints**: We use Python 3.12 type hints to make the code self-documenting.
- **Docstrings**: Crucial for AI Agents. If you write a tool, the docstring *is* the documentation for the AI.

---

## 🧪 4. Testing
- **Integration Tests**: We test the whole flow using the `Makefile` status report.
- **Unit Tests**: Place your unit tests in the root `/tests` directory (if you create it).
- **Manual Verification**: Before submitting, verify that your changes appear in the **NeuroTalk UI**.

---

## 📝 5. Documentation
We treat documentation as code. All documentation lives in the `/docs` directory. 
- Use GitHub Alerts (`> [!TIP]`, etc.) to highlight important info.
- Keep the language engaging and helpful.

---

> [!IMPORTANT]
> **No Secrets**: Never commit JSON credentials or API keys to the repository. The `.gitignore` is already set up to exclude them.
