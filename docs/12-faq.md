# ❓ FAQ

Quick answers to frequently asked questions about NeurOps.

## 1. General
### Can I use real hardware with NeurOps?
**Yes!** Simply point the `url` entries in `config.yaml` to your real iDRAC, iLO, or OpenBMC Redfish endpoints. You can skip the `neurosim/` layer entirely.

### Does it require a GPU?
**No.** All AI processing (Gemini) happens in the Google Cloud. Your local machine only needs to run the Python scripts and the Docker containers.

---

## 2. AI Assistant
### Why did the agent say it can't see server data?
This happens if `Neurosight` hasn't started polling yet or hasn't pushed data to BigQuery. Check `make status` to ensure all services are `RUNNING`.

### Can I use OpenAI instead of Gemini?
The current implementation uses the **Google ADK**, which is optimized for Google Gemini models. Swapping to OpenAI would require significant refactoring of the architecture.

---

## 3. Operations
### How do I reset the entire system?
Run `make stopneurops` followed by `make startneurops`. This will kill all processes and restart them from a clean state.

### The dashboard is empty. What's wrong?
1.  Check `logs/neurosight.log`.
2.  If you see "Offline" in the UI, it means `Neurosight` cannot reach the **Chaos Proxy** (Port 8080).
3.  Ensure you have run the [Docker Permission Fix](05-setup-guide.md).

---

## 4. Troubleshooting
### Why do I see "Image permission denied"?
You are likely on a Linux machine and your user is not in the `docker` group. Run the commands in the [Setup Guide](05-setup-guide.md) to fix this.

### Can I run this in Windows?
Yes, using **WSL2** (Windows Subsystem for Linux). Running directly on native Windows PowerShell is not currently supported by our `Makefile`.

---

> [!TIP]
> **Still stuck?** Open a diagnostic report by running `make status` and check the corresponding files in the `/logs` directory.
