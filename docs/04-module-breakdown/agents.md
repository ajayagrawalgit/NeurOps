# 🤖 Module Breakdown: NeuroTalk AI Assistant

**NeuroTalk** is the cognitive layer of NeurOps. While dashboards show you graphs, NeuroTalk gives you answers.

## 📁 Key Files
- `neurotalk/agent.py`: Agent definition (Name, Instruction, Tools).
- `neurotalk/tools.py`: Python functions the agent uses to "see" the world.
- `neurotalk/neurotalk_app.py`: The Streamlit chat UI.
- `helpers.py`: Contains the `run_agent()` shim for ADK execution.

---

## 🧠 1. The Agentic Brain
NeuroTalk is built using the **Google ADK (Agent Development Kit)**. Unlike a simple chatbot, an "Agent" is autonomous:
- It understands **Intent**: It knows if you're asking about right now (live) or the past (BigQuery).
- It uses **Tools**: It can browse your infrastructure logs and live metrics.
- It provides **Chain-of-Thought**: It explains *why* it reached a specific conclusion.

---

## 🛠️ 2. Agent Tools
The agent's power comes from its tools. If the agent didn't have tools, it would just be guessing. 

### `get_live_status()`
- **What it does**: Fetches the exact current reading from the Chaos Proxy.
- **When to use**: "How much CPU is being used right now?"

### `get_past_issues(device_id)`
- **What it does**: Executes a SQL query against **BigQuery** hardware telemetry tables.
- **When to use**: "Show me the last 10 anomalies for server-3."

---

## ⚙️ 3. Execution (The Shim)
The current version of the Google ADK requires a `Runner` to manage the interaction loop. 

Because Streamlit is synchronous but ADK is asynchronous, we use a **Shim** in `helpers.py` called `run_agent()`. This function:
1.  Creates an `InMemorySessionService`.
2.  Initializes an ADK `Runner`.
3.  Streams chunks of the LLM response until the text is complete.

---

## 🎨 4. User Interface
The **NeuroTalk UI** is a premium Streamlit application.
- **Sidebar**: Shows real-time server health (OK/Warning/Critical).
- **Chat Window**: Familiar messaging interface for natural language interaction.
- **Auto-Refresh**: The sidebar telemetry refreshes independently, keeping the dashboard alive while you chat.

---

## 💡 How to add new capabilities
To make NeuroTalk smarter:
1.  Define a new Python function in `tools.py`.
2.  Add a clear Docstring (this is how the AI knows what the tool does!).
3.  Add the function to the `tools` list in `agent.py`.

---

> [!TIP]
> **Pro-Tip**: Use the AI to ask questions that are hard to see on a graph. Try: *"Compare the temperature trends of server-1 and server-2 over the last hour."*
