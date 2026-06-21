from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import traceback
from identity.customer_identity import resolve_customer_id

GATEWAY_PORT = 9000
AGENT_BASE_URL = "http://127.0.0.1:8000"  # master_agent_api

app = FastAPI(title="Local API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    email: str      # from federated login
    message: str

@app.get("/health")
def health():
    return {"status": "gateway-up"}

@app.post("/chat")
async def chat(payload: ChatRequest):
    try:
        # Resolve identity here (Gateway responsibility)
        customer_id = resolve_customer_id(payload.email)
        print("EMAIL:", payload.email)
        print("RESOLVED CUSTOMER ID:", customer_id)

        # Do NOT forward email to agents
        agent_payload = {
            "customer_id": customer_id,
            "message": payload.message
        }

        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(
                f"{AGENT_BASE_URL}/chat",
                json=agent_payload
            )

        print("MASTER STATUS:", response.status_code)
        print("MASTER BODY:", response.text)

        return response.json()

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
