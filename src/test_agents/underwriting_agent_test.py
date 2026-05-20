import pytest

from agents.underwriting_agent import UnderwritingAgent


# Instantiate agent
underwriting_agent = UnderwritingAgent()


# ================================
# Test Case 1: Strong Profile → APPROVED
# ================================
def test_underwriting_approved():

    result = underwriting_agent.evaluate_application(
        customer_id="C001",
        credit_score=750,
        income_status="VERIFIED",
        emi_ratio=0.3
    )

    assert result["decision"] == "APPROVED"
    assert result["risk_level"] == "LOW"


# ================================
# Test Case 2: Income Not Verified → REJECTED
# ================================
def test_underwriting_income_failed():

    result = underwriting_agent.evaluate_application(
        customer_id="C002",
        credit_score=750,
        income_status="FAILED",
        emi_ratio=0.3
    )

    assert result["decision"] == "REJECTED"
    assert result["remarks"] == "Income verification failed"


# ================================
# Test Case 3: Very Low Credit Score → REJECTED
# ================================
def test_underwriting_low_credit():

    result = underwriting_agent.evaluate_application(
        customer_id="C003",
        credit_score=550,
        income_status="VERIFIED",
        emi_ratio=0.3
    )

    assert result["decision"] == "REJECTED"
    assert result["remarks"] == "Very low credit score"


# ================================
# Test Case 4: Borderline Credit → REVIEW
# ================================
def test_underwriting_borderline_review():

    result = underwriting_agent.evaluate_application(
        customer_id="C004",
        credit_score=650,
        income_status="VERIFIED",
        emi_ratio=0.3
    )

    assert result["decision"] == "REVIEW"
    assert result["risk_level"] == "MEDIUM"


# ================================
# Test Case 5: High EMI with Medium Credit → REJECTED
# ================================
def test_underwriting_high_emi_reject():

    result = underwriting_agent.evaluate_application(
        customer_id="C005",
        credit_score=650,
        income_status="VERIFIED",
        emi_ratio=0.6
    )

    assert result["decision"] == "REJECTED"
    assert result["remarks"] == "High EMI burden with low credit score"


# ================================
# Test Case 6: High EMI → REVIEW
# ================================
def test_underwriting_high_emi_review():

    result = underwriting_agent.evaluate_application(
        customer_id="C006",
        credit_score=720,
        income_status="VERIFIED",
        emi_ratio=0.45
    )

    assert result["decision"] == "REVIEW"
    assert result["risk_level"] == "MEDIUM"


# ================================
# Test Case 7: Missing EMI Ratio → REJECTED
# ================================
def test_underwriting_missing_emi():

    result = underwriting_agent.evaluate_application(
        customer_id="C007",
        credit_score=750,
        income_status="VERIFIED",
        emi_ratio=None
    )

    assert result["decision"] == "REJECTED"
    assert result["remarks"] == "Invalid EMI ratio"