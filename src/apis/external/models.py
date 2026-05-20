from pydantic import BaseModel
from datetime import date
from typing import List

# ----------------------------
# PAN MODELS (NO CHANGE)
# ----------------------------

class PANRequest(BaseModel):
    pan: str
    name: str
    dob: date


class PANResponse(BaseModel):
    status: str
    message: str


# ----------------------------
# BANK STATEMENT MODELS (NEW)
# ----------------------------

class Transaction(BaseModel):
    date: str
    amount: float
    description: str


class BankStatementRequest(BaseModel):
    customer_id: str


class BankStatementResponse(BaseModel):
    monthly_income: float
    emi_amount: float
    avg_balance: float
    transactions: List[Transaction]

class CreditScoreRequest(BaseModel):
    customer_id: str


class CreditScoreResponse(BaseModel):
    credit_score: int
    active_loans: int
    late_payments: int

class UnderwritingRequest(BaseModel):
    customer_id: str
    credit_score: int
    income_status: str
    emi_ratio: float | None


class UnderwritingResponse(BaseModel):
    decision: str
    risk_level: str
    remarks: str

