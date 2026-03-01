from fastapi import FastAPI
from .models import PANRequest, PANResponse
from .models import BankStatementRequest, BankStatementResponse
from .models import CreditScoreRequest, CreditScoreResponse
from identity.customer_identity import resolve_customer_id
from pydantic import BaseModel, EmailStr
import email_validator
from pathlib import Path
import json
import re

class CustomerIdentityRequest(BaseModel):
    email: EmailStr


class CustomerIdentityResponse(BaseModel):
    customer_id: str
    message: str

app = FastAPI(title="Dummy external services API", version="1.0")

# Load PAN data once at startup
with open("apis/external/data/pan.json", "r") as f:
    PAN_DB = json.load(f)

with open("apis/external/data/bank_statements.json", "r") as f:
    BANK_DB = json.load(f)

with open("apis/external/data/credit_scores.json", "r") as f:
    CREDIT_DB = json.load(f)

PAN_REGEX = r"^[A-Z]{5}[0-9]{4}[A-Z]$"

@app.post("/pan/verify", response_model=PANResponse)
def verify_pan(data: PANRequest):
    # Step 1: PAN format validation
    if not re.match(PAN_REGEX, data.pan):
        return PANResponse(
            status="FAILED",
            message="Invalid PAN format"
        )
    
    # Step 2: Search PAN in dummy DB
    record = next(
        (item for item in PAN_DB if item["pan"] == data.pan),
        None
    )

    if not record:
        return PANResponse(
            status="FAILED",
            message="PAN not found"
        )
    
    # Step 3: Name & DOB match
    if(
        record["name"].lower() != data.name.lower()
        or record["dob"] != str(data.dob)
    ):
        return PANResponse(
            status="FAILED",
            message="PAN details do not match"
        )
    
    # Step 4: Status check
    if record["status"] != "ACTIVE":
        return PANResponse(
            status="FAILED",
            message=f"PAN status is {record['status']}"
        )
    
    if record["status"] == "ACTIVE":    
        return PANResponse(
            status="VERIFIED",
            message="PAN verified successfully"
        )
    
    
@app.post("/bank-statements/fetch", response_model=BankStatementResponse)
def fetch_bank_statements(data: BankStatementRequest):

    record = BANK_DB.get(data.customer_id)

    if not record:
        return BankStatementResponse(
            monthly_income=0,
            emi_amount=0,
            avg_balance=0,
            transactions=[]
        )

    return BankStatementResponse(
        monthly_income=record["monthly_income"],
        emi_amount=record["emi_amount"],
        avg_balance=record["avg_balance"],
        transactions=record["transactions"]
    )

@app.post("/customer/resolve", response_model=CustomerIdentityResponse)
def resolve_customer(data: CustomerIdentityRequest):
    """
    Resolves or creates an internal customer ID
    from a federated login email.
    """

    customer_id = resolve_customer_id(data.email)

    return CustomerIdentityResponse(
        customer_id=customer_id,
        message="Customer ID resolved successfully"
    )

@app.post("/credit-score", response_model=CreditScoreResponse)
def fetch_credit_score(data: CreditScoreRequest):

    record = CREDIT_DB.get(data.customer_id)

    # If customer not found
    if not record:
        return CreditScoreResponse(
            credit_score=0,
            active_loans=0,
            late_payments=0
        )

    return CreditScoreResponse(
        credit_score=record["credit_score"],
        active_loans=record["active_loans"],
        late_payments=record["late_payments"]
    )