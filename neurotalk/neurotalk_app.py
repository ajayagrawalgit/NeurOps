import streamlit as st
import asyncio
import os
import sys
from datetime import datetime

# Ensure project root is in path to find helpers.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import agent
from tools import get_live_status

# --- Page Config ---
st.set_page_config(
    page_title="NeuroTalk | NeurOps",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Styling ---
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stChatMessage {
        border-radius: 15px;
        margin-bottom: 10px;
    }
    .stSidebar {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    h1, h2, h3 {
        color: #58a6ff;
        font-family: 'Inter', sans-serif;
    }
    .status-card {
        background: #1c2128;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
        margin-bottom: 10px;
    }
    .status-ok { color: #3fb950; }
    .status-warn { color: #d29922; }
    .status-crit { color: #f85149; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar: Server Status ---
with st.sidebar:
    st.image("https://img.icons8.com/isometric/512/brain.png", width=80)
    st.title("NeurOps | NeuroTalk")
    st.markdown("### 🖥️ Real-time Telemetry")
    
    status_data = get_live_status()
    st.markdown(f"**Total Servers:** `{len(status_data)}`")
    
    if st.button("🔄 Refresh Status", use_container_width=True):
        st.rerun()
    
    for server_id, data in status_data.items():
        with st.container():
            st.markdown(f"**{server_id}**")
            if "error" in data:
                st.error(f"Offline: {data['error']}")
            else:
                col1, col2 = st.columns(2)
                health = data.get("health", "Unknown")
                health_class = "status-ok" if health == "OK" else "status-warn" if health == "Warning" else "status-crit"
                
                st.markdown(f"<span class='{health_class}'>● {health}</span>", unsafe_allow_html=True)
                
                col1.metric("CPU", f"{data.get('cpu', 0)}%")
                col2.metric("Temp", f"{data.get('temp', 0)}°C")
            st.divider()

# --- Main App: NeuroTalk Chat ---
st.title("🧠 NeuroTalk")
st.caption("AI Infrastructure Assistant | Powered by Gemini 3 Flash")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm NeuroTalk. How can I help you with your infrastructure today?"}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask about system health, historical issues, or anomalies..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Analyzing telemetry data..."):
            try:
                # Use the run_agent helper to handle the ADK agent execution
                from helpers import run_agent
                full_response = asyncio.run(run_agent(agent, prompt))
                st.markdown(full_response)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.session_state.messages.append({"role": "assistant", "content": f"I encountered an error: {e}"})

# --- Footer ---
st.markdown("---")
st.markdown(f"**Last Sync:** {datetime.now().strftime('%H:%M:%S')}")
