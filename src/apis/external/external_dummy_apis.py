from fastapi import FastAPI
from .models import (
    PANRequest,
    PANResponse,
    BankStatementRequest,
    BankStatementResponse,
    CreditScoreRequest,
    CreditScoreResponse,
    UnderwritingRequest,
    UnderwritingResponse,
    PricingRequest,
    PricingResponse,
    SanctionLetterRequest,
    SanctionLetterResponse
)

from identity.customer_identity import resolve_customer_id

from pydantic import BaseModel, EmailStr

import email_validator
from pathlib import Path
from datetime import datetime

import json
import re
import uuid


# =====================================================
# CUSTOMER IDENTITY MODELS
# =====================================================

class CustomerIdentityRequest(BaseModel):
    email: EmailStr


class CustomerIdentityResponse(BaseModel):
    customer_id: str
    message: str


# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(
    title="Dummy External Services API",
    version="1.0"
)


# =====================================================
# LOAD DUMMY DATABASES
# =====================================================

with open("apis/external/data/pan.json", "r") as f:
    PAN_DB = json.load(f)

with open("apis/external/data/bank_statements.json", "r") as f:
    BANK_DB = json.load(f)

with open("apis/external/data/credit_scores.json", "r") as f:
    CREDIT_DB = json.load(f)

with open("apis/external/data/customers.json", "r") as f:
    CUSTOMER_DB = json.load(f)


# =====================================================
# REGEX
# =====================================================

PAN_REGEX = r"^[A-Z]{5}[0-9]{4}[A-Z]$"


# =====================================================
# PAN VERIFICATION API
# =====================================================

@app.post("/pan/verify", response_model=PANResponse)
def verify_pan(data: PANRequest):

    # Step 1: PAN format validation

    if not re.match(PAN_REGEX, data.pan):

        return PANResponse(
            status="FAILED",
            message="Invalid PAN format"
        )

    # Step 2: Search PAN in DB

    record = next(
        (
            item for item in PAN_DB
            if item["pan"] == data.pan
        ),
        None
    )

    if not record:

        return PANResponse(
            status="FAILED",
            message="PAN not found"
        )

    # Step 3: Name + DOB validation

    if (
        record["name"].lower() != data.name.lower()
        or record["dob"] != str(data.dob)
    ):

        return PANResponse(
            status="FAILED",
            message="PAN details do not match"
        )

    # Step 4: PAN status check

    if record["status"] != "ACTIVE":

        return PANResponse(
            status="FAILED",
            message=f"PAN status is {record['status']}"
        )

    # Success

    return PANResponse(
        status="VERIFIED",
        message="PAN verified successfully"
    )


# =====================================================
# BANK STATEMENT API
# =====================================================

@app.post(
    "/bank-statements/fetch",
    response_model=BankStatementResponse
)
def fetch_bank_statements(
    data: BankStatementRequest
):

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


# =====================================================
# CUSTOMER IDENTITY API
# =====================================================

@app.post(
    "/customer/resolve",
    response_model=CustomerIdentityResponse
)
def resolve_customer(
    data: CustomerIdentityRequest
):
    """
    Resolves or creates internal customer ID
    from federated login email.
    """

    customer_id = resolve_customer_id(
        data.email
    )

    return CustomerIdentityResponse(
        customer_id=customer_id,
        message="Customer ID resolved successfully"
    )


# =====================================================
# CREDIT SCORE API
# =====================================================

@app.post(
    "/credit-score",
    response_model=CreditScoreResponse
)
def fetch_credit_score(
    data: CreditScoreRequest
):

    record = CREDIT_DB.get(data.customer_id)

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


# =====================================================
# UNDERWRITING API
# =====================================================

@app.post(
    "/underwriting/evaluate",
    response_model=UnderwritingResponse
)
def underwriting_decision(
    data: UnderwritingRequest
):
    """
    Underwriting Rules

    1. Fetch credit score
    2. Reject if credit score < 700
    3. Approve if requested amount <= pre-approved limit
    4. If <= 2x pre-approved:
       require salary slip
       approve if EMI <= 50% salary
    5. Reject otherwise
    """

    # --------------------------------
    # Fetch credit score from DB
    # --------------------------------

    record = CREDIT_DB.get(
        data.customer_id
    )

    if not record:

        return UnderwritingResponse(
            decision="REJECTED",
            credit_score=0,
            remarks="Credit score not found"
        )

    credit_score = record["credit_score"]

    # --------------------------------
    # Rule 1
    # --------------------------------

    if credit_score < 700:

        return UnderwritingResponse(
            decision="REJECTED",
            credit_score=credit_score,
            remarks="Credit score below minimum threshold"
        )

    # --------------------------------
    # Rule 2
    # --------------------------------

    if (
        data.requested_loan_amount
        <= data.preapproved_limit
    ):

        return UnderwritingResponse(
            decision="APPROVED",
            credit_score=credit_score,
            remarks="Within pre-approved limit"
        )

    # --------------------------------
    # Rule 3
    # --------------------------------

    if (
        data.requested_loan_amount
        <= 2 * data.preapproved_limit
    ):

        if data.monthly_salary is None:

            return UnderwritingResponse(
                decision="PENDING_DOCUMENT",
                credit_score=credit_score,
                remarks="Salary slip required"
            )

        if data.expected_emi is None:

            return UnderwritingResponse(
                decision="REJECTED",
                credit_score=credit_score,
                remarks="Expected EMI missing"
            )

        if (
            data.expected_emi
            <= data.monthly_salary * 0.5
        ):

            return UnderwritingResponse(
                decision="APPROVED",
                credit_score=credit_score,
                remarks="Approved after salary verification"
            )

        return UnderwritingResponse(
            decision="REJECTED",
            credit_score=credit_score,
            remarks="EMI exceeds 50% of salary"
        )

    # --------------------------------
    # Rule 4
    # --------------------------------

    return UnderwritingResponse(
        decision="REJECTED",
        credit_score=credit_score,
        remarks="Requested amount exceeds underwriting limit"
    )


# =====================================================
# PRICING API
# =====================================================

@app.post(
    "/pricing/calculate",
    response_model=PricingResponse
)
def calculate_pricing(
    data: PricingRequest
):
    """
    Simulates loan pricing engine.
    """

    credit_score = data.credit_score
    monthly_income = data.monthly_income
    existing_emi = data.existing_emi

    # EMI Ratio

    emi_ratio = existing_emi / monthly_income

    # EMI burden check

    if emi_ratio > 0.6:

        return PricingResponse(
            pricing_status="REJECTED",
            interest_rate=0,
            eligible_loan_amount=0,
            tenure_months=0,
            estimated_emi=0,
            remarks="Existing EMI burden too high"
        )

    # Interest rate logic

    if credit_score >= 800:
        interest_rate = 10.5

    elif credit_score >= 750:
        interest_rate = 11.5

    elif credit_score >= 700:
        interest_rate = 12.5

    elif credit_score >= 650:
        interest_rate = 14.0

    else:

        return PricingResponse(
            pricing_status="REJECTED",
            interest_rate=0,
            eligible_loan_amount=0,
            tenure_months=0,
            estimated_emi=0,
            remarks="Credit score too low"
        )

    # Eligible EMI

    eligible_emi = (
        monthly_income * 0.5
    ) - existing_emi

    if eligible_emi <= 0:

        return PricingResponse(
            pricing_status="REJECTED",
            interest_rate=0,
            eligible_loan_amount=0,
            tenure_months=0,
            estimated_emi=0,
            remarks="Insufficient repayment capacity"
        )

    # Tenure

    if credit_score >= 750:
        tenure_months = 84

    elif credit_score >= 700:
        tenure_months = 60

    else:
        tenure_months = 36

    # Loan amount

    eligible_loan_amount = (
        eligible_emi * tenure_months
    )

    estimated_emi = (
        eligible_loan_amount / tenure_months
    )

    return PricingResponse(
        pricing_status="APPROVED",
        interest_rate=interest_rate,
        eligible_loan_amount=round(
            eligible_loan_amount,
            2
        ),
        tenure_months=tenure_months,
        estimated_emi=round(
            estimated_emi,
            2
        ),
        remarks="Loan pricing calculated successfully"
    )


# =====================================================
# SANCTION LETTER API
# =====================================================

@app.post(
    "/sanction-letter/generate",
    response_model=SanctionLetterResponse
)
def generate_sanction_letter(
    data: SanctionLetterRequest
):
    """
    Generates loan sanction letter.
    """

    # Validation

    if data.underwriting_decision != "APPROVED":

        return SanctionLetterResponse(
            sanction_status="FAILED",
            sanction_id="",
            sanction_letter="",
            remarks=(
                "Loan not approved by underwriting"
            )
        )

    if data.pricing_status != "APPROVED":

        return SanctionLetterResponse(
            sanction_status="FAILED",
            sanction_id="",
            sanction_letter="",
            remarks=(
                "Pricing approval not available"
            )
        )

    # Generate sanction details

    sanction_id = (
        f"SAN-{uuid.uuid4().hex[:8].upper()}"
    )

    sanction_date = datetime.now().strftime(
        "%Y-%m-%d"
    )

    # EMI Calculation

    monthly_interest = (
        data.interest_rate / 12 / 100
    )

    estimated_emi = (
        data.loan_amount
        * monthly_interest
        * ((1 + monthly_interest)
        ** data.tenure_months)
    ) / (
        ((1 + monthly_interest)
        ** data.tenure_months) - 1
    )

    # Generate sanction letter

    sanction_letter = f"""
==================================================
              LOAN SANCTION LETTER
==================================================

Sanction ID      : {sanction_id}
Date             : {sanction_date}

Customer ID      : {data.customer_id}
Customer Name    : {data.customer_name}

--------------------------------------------------
LOAN DETAILS
--------------------------------------------------

Approved Loan Amount : ₹{data.loan_amount:,.2f}

Interest Rate        : {data.interest_rate}%

Loan Tenure          : {data.tenure_months} months

Estimated EMI        : ₹{estimated_emi:,.2f}

--------------------------------------------------
STATUS
--------------------------------------------------

Loan Status : SANCTIONED

==================================================
"""

    return SanctionLetterResponse(
        sanction_status="APPROVED",
        sanction_id=sanction_id,
        sanction_letter=sanction_letter,
        remarks="Sanction letter generated successfully"
    )