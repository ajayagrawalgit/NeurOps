PYTHON = /home/mickey/DevSpace/mylab/bin/python3
UVICORN = /home/mickey/DevSpace/mylab/bin/uvicorn

.PHONY: startneurosight stopneurosight startneuriosim stopneuriosim startchaosrouters stopchaosrouters startneurotalk stopneurotalk

startneurosight:
	@echo "🚀 Starting Neurosight..."
	@nohup $(PYTHON) neurosight/neurosight.py > neurosight.log 2>&1 & echo $$! > neurosight.pid
	@echo "✅ Neurosight started."

stopneurosight:
	@echo "🛑 Stopping Neurosight..."
	@if [ -f neurosight.pid ]; then kill $$(cat neurosight.pid) 2>/dev/null && rm neurosight.pid; else pkill -f neurosight.py || true; fi
	@echo "✅ Neurosight stopped."

startneuriosim:
	@echo "🚀 Starting Neurosim (Docker Compose)..."
	@docker compose -f neurosim/docker-compose.yml up -d
	@echo "✅ Neurosim started."

stopneuriosim:
	@echo "🛑 Stopping Neurosim (Docker Compose)..."
	@docker compose -f neurosim/docker-compose.yml down
	@echo "✅ Neurosim stopped."

startchaosrouters:
	@echo "🚀 Starting Chaos Routers (FastAPI)..."
	@nohup $(UVICORN) neurosim.chaos_management_routers:app --host 0.0.0.0 --port 8080 > chaos.log 2>&1 & echo $$! > chaos.pid
	@echo "✅ Chaos Routers started."

stopchaosrouters:
	@echo "🛑 Stopping Chaos Routers..."
	@if [ -f chaos.pid ]; then kill $$(cat chaos.pid) 2>/dev/null && rm chaos.pid; else pkill -f chaos_management_routers || true; fi
	@echo "✅ Chaos Routers stopped."

startneurotalk:
	@echo "🚀 Starting NeuroTalk (Streamlit)..."
	@nohup $(PYTHON) -m streamlit run neurotalk_app.py --server.port 8501 > neurotalk.log 2>&1 & echo $$! > neurotalk.pid
	@echo "✅ NeuroTalk started."

stopneurotalk:
	@echo "🛑 Stopping NeuroTalk..."
	@if [ -f neurotalk.pid ]; then kill $$(cat neurotalk.pid) 2>/dev/null && rm neurotalk.pid; else pkill -f streamlit || true; fi
	@echo "✅ NeuroTalk stopped."
