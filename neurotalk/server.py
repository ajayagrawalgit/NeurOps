from fastapi import FastAPI
from pydantic import BaseModel

from neurotalk.agent import agent

app = FastAPI(title="NeuroTalk ADK")


class Query(BaseModel):
    question: str


@app.post("/ask")
async def ask(q: Query):
    response = await agent.run(q.question)
    return {"answer": response.output_text}


@app.get("/")
def root():
    return {"message": "NeuroTalk (ADK) is alive 🧠🔥"}