from fastapi import FastAPI
from pydantic import BaseModel
from agents.master_agent import MasterAgent

app = FastAPI(title="Master Agent API")

agent = MasterAgent()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    return {"reply": agent.run(req.message)}
