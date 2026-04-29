# 🛠️ Manual Service Management Guide

So you want to get your hands dirty and run the NeurOps services individually? We've got you covered! While our `Makefile` is super handy, sometimes you just want to see what's happening under the hood or run things in a specific way. 🚀

This guide lists every single command you'll need to start and stop the individual parts of the NeurOps ecosystem, accompanied by quick video demos to show you exactly how it looks!

---

## 📡 1. Neurosight Collector
This is the brain that gathers telemetry from all your servers.

### 🚀 To Start:
```bash
# Make sure your virtual environment is active!
python neurosight/neurosight.py
```

> [!NOTE]
> If you want to run it in the background, you can use `nohup`:
> `nohup python neurosight/neurosight.py >> logs/neurosight.log 2>&1 &`

#### 📺 Watch it in action:
https://github.com/user-attachments/assets/7d775823-8a78-44fd-8dfe-c8060136aa8d

### 🛑 To Stop:
If you ran it in the foreground, just hit `Ctrl+C`. If it's in the background, you can find the process and kill it:
```bash
pkill -f neurosight.py
```

---

## 🐳 2. Neurosim (Redfish Simulators)
These are the Docker containers that mimic real hardware.

> [!IMPORTANT]
> This is a development environment, so you will see development containers. However, NeurOps is production-ready! It has been tested in real-world environments spanning across different regions with over 100 hardware assets. 🌍

### 🚀 To Start:
```bash
docker compose -f neurosim/docker-compose.yml up
```

#### 📺 Watch it in action:
https://github.com/user-attachments/assets/98b21de0-d63c-4c2e-b15e-5c4420671bed

### 🛑 To Stop:
Just press `Ctrl+C` if running in the foreground. If you are running with `-d`, execute this command from the root of the repository:
```bash
docker compose -f neurosim/docker-compose.yml down
```

---

## 🌀 3. Chaos Management Routers
This FastAPI app handles chaos injection and auto-healing hooks. You can use `curl` commands from your terminal, or use the beautiful Swagger UI!

### 🚀 To Start:
```bash
uvicorn neurosim.chaos_management_routers:app --host 0.0.0.0 --port 8080
```

#### 📺 Starting the Routers:
https://github.com/user-attachments/assets/775c4fe4-5875-4586-aa8a-e62f35988a9d

#### 📺 Using the Swagger UI for Chaos Injection:
https://github.com/user-attachments/assets/e1874d56-0918-421c-95b5-766228dd6546

### 🛑 To Stop:
Hit `Ctrl+C` in the terminal where it's running, or use:
```bash
pkill -f chaos_management_routers
```

---

## 🧠 4. NeuroTalk UI (Streamlit)
The chatbot where you can literally talk to your infrastructure! ╰(*°▽°*)╯

### 🚀 To Start:
```bash
streamlit run neurotalk/neurotalk_app.py --server.port 8501
```

#### 📺 Watch the UI in action:
https://github.com/user-attachments/assets/cf0b9330-9a75-4c46-90d4-eba2fc44dce9

#### 📺 Full Workflow Demo:
https://github.com/user-attachments/assets/054dc5ca-aac0-4348-96e6-b64c19190700

### 🛑 To Stop:
Hit `Ctrl+C` in the terminal, or use:
```bash
pkill -f streamlit
```

---

## 💡 Pro-Tips for Manual Management
- **Logs**: If you run things manually in separate terminals, you'll see the logs right there! It's great for debugging. 🔍
- **Order Matters**: Usually, you'll want to start the Simulators first, then the Chaos Routers, then Neurosight, and finally the UI. 🚦
- **Environment**: Always double-check that your virtual environment in which all your packages are installed is active before running the Python commands.

Happy hacking! 👩‍💻👨‍💻
