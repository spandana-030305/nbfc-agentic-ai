from pydantic import BaseModel
from datetime import date
from typing import List, Optional


# ----------------------------
# PAN MODELS
# ----------------------------

class PANRequest(BaseModel):
    pan: str
    name: str
    dob: date


class PANResponse(BaseModel):
    status: str
    message: str


# ----------------------------
# BANK STATEMENT MODELS
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


# ----------------------------
# CREDIT SCORE MODELS
# ----------------------------

class CreditScoreRequest(BaseModel):
    customer_id: str


class CreditScoreResponse(BaseModel):
    credit_score: int
    active_loans: int
    late_payments: int


# ----------------------------
# CRM MODELS
# ----------------------------

class CRMRequest(BaseModel):
    customer_id: str


class CRMResponse(BaseModel):
    crm_verification_status: str
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    message: str


# ----------------------------
# eSIGN MODELS
# ----------------------------

class eSignRequest(BaseModel):
    customer_id: str
    customer_name: str
    loan_amount: float
    sanction_id: str


class eSignResponse(BaseModel):
    sign_status: str
    signature_id: Optional[str] = None
    signed_at: Optional[str] = None
    documents: List[str] = []
    message: str


# ----------------------------
# DISBURSEMENT MODELS
# ----------------------------

class DisbursementRequest(BaseModel):
    customer_id: str
    customer_name: str
    loan_amount: float
    sanction_id: str
    signature_id: str


class DisbursementResponse(BaseModel):
    disbursement_status: str
    disbursement_id: Optional[str] = None
    amount_disbursed: float = 0
    processing_time: Optional[str] = None
    bank_reference: Optional[str] = None
    expected_credit_date: Optional[str] = None
    message: str


# ----------------------------
# UNDERWRITING MODELS
# (updated according to new rules)
# ----------------------------

class UnderwritingRequest(BaseModel):
    customer_id: str
    requested_loan_amount: float
    preapproved_limit: float
    monthly_salary: Optional[float] = None
    expected_emi: Optional[float] = None


class UnderwritingResponse(BaseModel):
    decision: str
    credit_score: int
    remarks: str


# ----------------------------
# PRICING AGENT MODELS
# ----------------------------

class PricingRequest(BaseModel):
    customer_id: str
    requested_loan_amount: float
    credit_score: int
    tenure_months: int


class PricingResponse(BaseModel):
    pricing_status: str
    interest_rate: float
    approved_amount: float
    tenure_months: int
    estimated_emi: float
    remarks: str


# ----------------------------
# SANCTION LETTER MODELS
# ----------------------------

class SanctionLetterRequest(BaseModel):
    customer_id: str
    customer_name: str
    loan_amount: float
    interest_rate: float
    tenure_months: int
    underwriting_decision: str
    pricing_status: str


class SanctionLetterResponse(BaseModel):
    sanction_status: str
    sanction_id: str
    customer_id: str
    customer_name: str
    loan_amount: float
    interest_rate: float
    tenure_months: int
    estimated_emi: float
    generated_on: str
    pdf_path: str
    sanction_letter: str
    remarks: str