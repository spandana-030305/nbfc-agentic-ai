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

