from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import traceback
import os
import shutil
from datetime import datetime
from identity.customer_identity import resolve_customer_id
from utils.memory import get_shared_memory

GATEWAY_PORT = 9000
AGENT_BASE_URL = "http://127.0.0.1:8000"  # master_agent_api

# Document storage configuration
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

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

class UploadResponse(BaseModel):
    status: str
    filename: str
    filepath: str
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


@app.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    email: str = Form(...),
    document_type: str = Form(default="salary_slip")
):
    """
    Upload salary slip or other documents for loan verification.
    Stores file and notifies underwriting agent.
    """
    try:
        # Resolve customer
        customer_id = resolve_customer_id(email)
        print(f"FILE UPLOAD - Customer: {customer_id}, Email: {email}")

        # Create customer-specific directory
        customer_dir = os.path.join(UPLOAD_DIR, customer_id)
        os.makedirs(customer_dir, exist_ok=True)

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{document_type}_{timestamp}_{file.filename}"
        filepath = os.path.join(customer_dir, filename)

        # Save file
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"FILE SAVED: {filepath}")

        # Store in shared memory
        memory = get_shared_memory()
        memory.store_document(document_type, filepath)
        memory.update_workflow_state("salary_slip_uploaded", True)
        memory.add_message(
            role="system",
            content=f"Document uploaded: {filename}",
            agent_name="gateway"
        )

        # Notify master agent about upload
        agent_payload = {
            "customer_id": customer_id,
            "message": f"Salary slip uploaded successfully. Please proceed with underwriting."
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            agent_response = await client.post(
                f"{AGENT_BASE_URL}/chat",
                json=agent_payload
            )

        return UploadResponse(
            status="success",
            filename=filename,
            filepath=filepath,
            message=f"Document uploaded and processed. {agent_response.json().get('reply', '')}"
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents/{customer_id}")
async def get_documents(customer_id: str):
    """Retrieve all uploaded documents for a customer"""
    try:
        customer_dir = os.path.join(UPLOAD_DIR, customer_id)

        if not os.path.exists(customer_dir):
            return {"documents": []}

        documents = []
        for file in os.listdir(customer_dir):
            filepath = os.path.join(customer_dir, file)
            documents.append({
                "filename": file,
                "path": filepath,
                "uploaded_at": datetime.fromtimestamp(
                    os.path.getctime(filepath)
                ).isoformat()
            })

        return {"documents": documents}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
