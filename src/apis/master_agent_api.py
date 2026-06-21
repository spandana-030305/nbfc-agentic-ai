from fastapi import FastAPI
from pydantic import BaseModel
from agents.master_agent import MasterAgent

app = FastAPI(title="Master Agent API")

agent = MasterAgent()


# Accept BOTH customer_id and message
class ChatRequest(BaseModel):
    customer_id: str
    message: str


@app.post("/chat")
def chat(req: ChatRequest):
    print("MASTER RECEIVED CUSTOMER_ID:", req.customer_id)
    return {
        "reply": agent.run(
            user_message=req.message,
            customer_id=req.customer_id
        )
    }
