from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import traceback

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
    message: str

@app.get("/health")
def health():
    return {"status": "gateway-up"}

@app.post("/chat")
async def chat(payload: ChatRequest):
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{AGENT_BASE_URL}/chat",
                json=payload.dict()
            )

        print("MASTER STATUS:", response.status_code)
        print("MASTER BODY:", response.text)

        return response.json()

    except httpx.RequestError as e:
        print("REQUEST ERROR:", repr(e))
        traceback.print_exc()
        raise HTTPException(
            status_code=502,
            detail=f"Agent service unreachable: {str(e)}"
        )

    except Exception as e:
        print("GENERAL ERROR:", repr(e))
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )