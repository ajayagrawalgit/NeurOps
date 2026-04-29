# 🛠️ Manual Service Management Guide

So you want to get your hands dirty and run the NeurOps services individually? We've got you covered! While our `Makefile` is super handy, sometimes you just want to see what's happening under the hood or run things in a specific way. 🚀

This guide lists every single command you'll need to start and stop the individual parts of the NeurOps ecosystem.

---

## 📡 1. Neurosight Collector
This is the brain that gathers telemetry from all your servers.

### 🚀 To Start:
```bash
# Make sure your virtual environment is active!
python neurosight/neurosight.py
```
*Note: If you want to run it in the background, you can use `nohup` like this:*
`nohup python neurosight/neurosight.py >> logs/neurosight.log 2>&1 &`

### 🛑 To Stop:
If you ran it in the foreground, just hit `Ctrl+C`. If it's in the background, you can find the process and kill it:
```bash
pkill -f neurosight.py
```

---

## 🐳 2. Neurosim (Redfish Simulators)
These are the Docker containers that mimic real hardware.

### 🚀 To Start:
```bash
docker compose -f neurosim/docker-compose.yml up -d
```

### 🛑 To Stop:
```bash
docker compose -f neurosim/docker-compose.yml down
```

---

## 🌀 3. Chaos Management Routers
This FastAPI app handles the chaos injection and auto-healing hooks.

### 🚀 To Start:
```bash
uvicorn neurosim.chaos_management_routers:app --host 0.0.0.0 --port 8080
```

### 🛑 To Stop:
Hit `Ctrl+C` in the terminal where it's running, or use:
```bash
pkill -f chaos_management_routers
```

---

## 🧠 4. NeuroTalk UI (Streamlit)
The beautiful dashboard where you chat with your infrastructure!

### 🚀 To Start:
```bash
streamlit run neurotalk/neurotalk_app.py --server.port 8501
```

### 🛑 To Stop:
Hit `Ctrl+C` in the terminal, or use:
```bash
pkill -f streamlit
```

---

## 💡 Pro-Tips for Manual Management
- **Logs**: If you run things manually in separate terminals, you'll see the logs right there! It's great for debugging. 🔍
- **Order Matters**: Usually, you'll want to start the Simulators first, then the Chaos Routers, then Neurosight, and finally the UI. 🚦
- **Environment**: Always double-check that your `mylab` virtual environment is active before running the Python commands.

Happy hacking! 👩‍💻👨‍💻
