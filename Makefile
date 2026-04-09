PYTHON = /home/mickey/DevSpace/mylab/bin/python3
UVICORN = /home/mickey/DevSpace/mylab/bin/uvicorn
LOG_DIR = logs

.PHONY: startneurosight stopneurosight startneuriosim stopneuriosim startchaosrouters stopchaosrouters startneurotalk stopneurotalk init-logs startneurops stopneurops status check-docker

init-logs:
	@mkdir -p $(LOG_DIR)

startneurosight: init-logs
	@echo "🚀 Starting Neurosight..."
	@nohup $(PYTHON) neurosight/neurosight.py >> $(LOG_DIR)/neurosight.log 2>&1 & echo $$! > $(LOG_DIR)/neurosight.pid
	@echo "✅ Neurosight started."

stopneurosight:
	@echo "🛑 Stopping Neurosight..."
	@if [ -f $(LOG_DIR)/neurosight.pid ]; then kill $$(cat $(LOG_DIR)/neurosight.pid) 2>/dev/null && rm $(LOG_DIR)/neurosight.pid; else pkill -f neurosight.py || true; fi
	@echo "✅ Neurosight stopped."

startneuriosim:
	@echo "🚀 Starting Neurosim (Docker Compose)..."
	@docker compose -f neurosim/docker-compose.yml up -d
	@echo "✅ Neurosim started."

stopneuriosim:
	@echo "🛑 Stopping Neurosim (Docker Compose)..."
	@docker compose -f neurosim/docker-compose.yml down
	@echo "✅ Neurosim stopped."

startchaosrouters: init-logs
	@echo "🚀 Starting Chaos Routers (FastAPI)..."
	@nohup $(UVICORN) neurosim.chaos_management_routers:app --host 0.0.0.0 --port 8080 >> $(LOG_DIR)/chaos.log 2>&1 & echo $$! > $(LOG_DIR)/chaos.pid
	@echo "✅ Chaos Routers started."

stopchaosrouters:
	@echo "🛑 Stopping Chaos Routers..."
	@if [ -f $(LOG_DIR)/chaos.pid ]; then kill $$(cat $(LOG_DIR)/chaos.pid) 2>/dev/null && rm $(LOG_DIR)/chaos.pid; else pkill -f chaos_management_routers || true; fi
	@echo "✅ Chaos Routers stopped."

startneurotalk: init-logs
	@echo "🚀 Starting NeuroTalk (Streamlit)..."
	@nohup $(PYTHON) -m streamlit run neurotalk/neurotalk_app.py --server.port 8501 >> $(LOG_DIR)/neurotalk.log 2>&1 & echo $$! > $(LOG_DIR)/neurotalk.pid
	@echo "✅ NeuroTalk started."

stopneurotalk:
	@echo "🛑 Stopping NeuroTalk..."
	@if [ -f $(LOG_DIR)/neurotalk.pid ]; then kill $$(cat $(LOG_DIR)/neurotalk.pid) 2>/dev/null && rm $(LOG_DIR)/neurotalk.pid; else pkill -f streamlit || true; fi
	@echo "✅ NeuroTalk stopped."

check-docker:
	@docker ps >/dev/null 2>&1 || (printf "\n\033[0;31m❌ DOCKER PERMISSION ERROR\033[0m\n"; \
	echo "Your user '$(USER)' is not in the 'docker' group."; \
	echo "Please run the following commands to fix this:"; \
	echo "  sudo usermod -aG docker $(USER)"; \
	echo "  newgrp docker"; \
	exit 1)

startneurops: init-logs check-docker
	@echo "\n🧠 Starting NeurOps Ecosystem..."
	@echo "------------------------------------------------------------"
	@echo "1️⃣  Starting Redfish Simulators (Sequential)..."
	@for i in 1 2 3; do \
		echo "   ⚡ Starting redfish-$$i..."; \
		docker compose -f neurosim/docker-compose.yml up -d redfish-$$i; \
		sleep 2; \
	done
	@echo "2️⃣  Starting Neurosight.py..."
	@$(MAKE) startneurosight
	@sleep 3
	@echo "3️⃣  Starting Chaos Management Routers..."
	@$(MAKE) startchaosrouters
	@sleep 3
	@echo "4️⃣  Starting NeuroTalk UI..."
	@$(MAKE) startneurotalk
	@sleep 2
	@echo "------------------------------------------------------------"
	@echo "✅ NeurOps Ecosystem is UP and Running!"
	@$(MAKE) status

stopneurops:
	@echo "\n🛑 Shutting down NeurOps Ecosystem..."
	@$(MAKE) stopneurotalk
	@$(MAKE) stopchaosrouters
	@$(MAKE) stopneurosight
	@$(MAKE) stopneuriosim
	@echo "✅ All services stopped."

status:
	@echo "\n📊 NEUROPS SERVICE STATUS REPORT"
	@echo "============================================================"
	@printf "%-20s %-10s %-10s %-20s\n" "SERVICE" "PID" "STATUS" "LOG FILE"
	@echo "------------------------------------------------------------"
	@# Neurosight
	@if [ -f $(LOG_DIR)/neurosight.pid ] && kill -0 $$(cat $(LOG_DIR)/neurosight.pid) 2>/dev/null; then \
		printf "\033[0;32m%-20s\033[0m %-10s %-10s %-20s\n" "Neurosight" "$$(cat $(LOG_DIR)/neurosight.pid)" "RUNNING" "$(LOG_DIR)/neurosight.log"; \
	else \
		printf "\033[0;31m%-20s\033[0m %-10s %-10s %-20s\n" "Neurosight" "N/A" "STOPPED" "$(LOG_DIR)/neurosight.log"; \
	fi
	@# Chaos Routers
	@if [ -f $(LOG_DIR)/chaos.pid ] && kill -0 $$(cat $(LOG_DIR)/chaos.pid) 2>/dev/null; then \
		printf "\033[0;32m%-20s\033[0m %-10s %-10s %-20s\n" "Chaos Routers" "$$(cat $(LOG_DIR)/chaos.pid)" "RUNNING" "$(LOG_DIR)/chaos.log"; \
	else \
		printf "\033[0;31m%-20s\033[0m %-10s %-10s %-20s\n" "Chaos Routers" "N/A" "STOPPED" "$(LOG_DIR)/chaos.log"; \
	fi
	@# NeuroTalk
	@if [ -f $(LOG_DIR)/neurotalk.pid ] && kill -0 $$(cat $(LOG_DIR)/neurotalk.pid) 2>/dev/null; then \
		printf "\033[0;32m%-20s\033[0m %-10s %-10s %-20s\n" "NeuroTalk UI" "$$(cat $(LOG_DIR)/neurotalk.pid)" "RUNNING" "$(LOG_DIR)/neurotalk.log"; \
	else \
		printf "\033[0;31m%-20s\033[0m %-10s %-10s %-20s\n" "NeuroTalk UI" "N/A" "STOPPED" "$(LOG_DIR)/neurotalk.log"; \
	fi
	@# Redfish Simulators
	@for i in 1 2 3; do \
		CONTAINER="redfish_$$i"; \
		STATUS=$$(docker inspect --format '{{.State.Status}}' $$CONTAINER 2>/dev/null || echo "stopped"); \
		if [ "$$STATUS" = "running" ]; then \
			PID=$$(docker inspect --format '{{.State.Pid}}' $$CONTAINER 2>/dev/null || echo "N/A"); \
			printf "\033[0;36m%-20s\033[0m %-10s %-10s %-20s\n" "Redfish-$$i" "$$PID" "RUNNING" "Docker"; \
		else \
			printf "\033[0;31m%-20s\033[0m %-10s %-10s %-20s\n" "Redfish-$$i" "N/A" "STOPPED" "Docker"; \
		fi; \
	done
	@echo "============================================================"
