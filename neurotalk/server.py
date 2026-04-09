from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neurotalk.agent import agent
from helpers import run_agent

app = FastAPI()

class Query(BaseModel):
    question: str

@app.post("/ask")
async def ask(q: Query):
    # response = await agent.run(q.question)
    response_text = await run_agent(agent, q.question)
    return {"answer": response_text}

@app.get("/")
async def root():
    return {"message": "NeuroTalk Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)