from google.adk.agents import Agent
from google.adk.models import Gemini

from neurotalk.tools import get_live_status, get_past_issues


agent = Agent(
    name="NeuroTalk",
    model=Gemini(model="gemini-3-flash-preview"),

    tools=[
        get_live_status,
        get_past_issues
    ],

    instruction="""
You are NeuroTalk, an AI infrastructure assistant.

You help users:
- Understand current system health
- Analyze historical issues
- Detect anomalies and trends

Tool usage:
- Use get_live_status() for real-time questions
- Use get_past_issues(device_id) for historical queries
- Combine both when needed

Always explain insights clearly, not just raw data.
"""
)

root_agent = agent