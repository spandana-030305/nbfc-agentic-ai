import pytest

from agents.sanction_letter_agent import (
    SanctionLetterAgent
)

# Instantiate agent
sanction_agent = SanctionLetterAgent()


# ==================================================
# Test Case 1:
# Valid Approved Loan → SANCTION APPROVED
# ==================================================

def test_sanction_letter_approved():

    result = sanction_agent.generate_sanction_letter(
        customer_id="C001",
        customer_name="Sai Spandana",
        loan_amount=1500000,
        interest_rate=11.5,
        tenure_months=60,
        underwriting_decision="APPROVED",
        pricing_status="APPROVED"
    )

    assert result["sanction_status"] == "APPROVED"

    assert result["customer_id"] == "C001"

    assert result["loan_amount"] == 1500000

    assert "sanction_letter" in result

    assert "LOAN SANCTION LETTER" in (
        result["sanction_letter"]
    )


# ==================================================
# Test Case 2:
# Underwriting Rejected → SANCTION FAILED
# ==================================================

def test_sanction_letter_underwriting_failed():

    result = sanction_agent.generate_sanction_letter(
        customer_id="C002",
        customer_name="Rahul",
        loan_amount=1000000,
        interest_rate=12.5,
        tenure_months=48,
        underwriting_decision="REJECTED",
        pricing_status="APPROVED"
    )

    assert result["sanction_status"] == "FAILED"

    assert result["remarks"] == (
        "Loan not approved by underwriting"
    )


# ==================================================
# Test Case 3:
# Pricing Failed → SANCTION FAILED
# ==================================================

def test_sanction_letter_pricing_failed():

    result = sanction_agent.generate_sanction_letter(
        customer_id="C003",
        customer_name="Anjali",
        loan_amount=800000,
        interest_rate=13.0,
        tenure_months=36,
        underwriting_decision="APPROVED",
        pricing_status="FAILED"
    )

    assert result["sanction_status"] == "FAILED"

    assert result["remarks"] == (
        "Pricing approval not available"
    )


# ==================================================
# Test Case 4:
# Pricing Rejected → SANCTION FAILED
# ==================================================

def test_sanction_letter_pricing_rejected():

    result = sanction_agent.generate_sanction_letter(
        customer_id="C004",
        customer_name="Kiran",
        loan_amount=500000,
        interest_rate=14.0,
        tenure_months=24,
        underwriting_decision="APPROVED",
        pricing_status="REJECTED"
    )

    assert result["sanction_status"] == "FAILED"

    assert result["remarks"] == (
        "Pricing approval not available"
    )


# ==================================================
# Test Case 5:
# EMI Calculation Validation
# ==================================================

def test_sanction_letter_emi_generated():

    result = sanction_agent.generate_sanction_letter(
        customer_id="C005",
        customer_name="Meghana",
        loan_amount=1200000,
        interest_rate=10.5,
        tenure_months=72,
        underwriting_decision="APPROVED",
        pricing_status="APPROVED"
    )

    assert result["sanction_status"] == "APPROVED"

    assert result["estimated_emi"] > 0


# ==================================================
# Test Case 6:
# Sanction ID Generation
# ==================================================

def test_sanction_id_generated():

    result = sanction_agent.generate_sanction_letter(
        customer_id="C006",
        customer_name="Arjun",
        loan_amount=2000000,
        interest_rate=11.0,
        tenure_months=84,
        underwriting_decision="APPROVED",
        pricing_status="APPROVED"
    )

    assert result["sanction_status"] == "APPROVED"

    assert result["sanction_id"].startswith("SAN-")


# ==================================================
# Test Case 7:
# Sanction Letter Contains Customer Details
# ==================================================

def test_sanction_letter_contains_customer_info():

    result = sanction_agent.generate_sanction_letter(
        customer_id="C007",
        customer_name="Priya",
        loan_amount=900000,
        interest_rate=12.0,
        tenure_months=48,
        underwriting_decision="APPROVED",
        pricing_status="APPROVED"
    )

    sanction_letter = result["sanction_letter"]

    assert "Priya" in sanction_letter

    assert "C007" in sanction_letter

    assert "900000" in sanction_letter or "9,00,000" in sanction_letter