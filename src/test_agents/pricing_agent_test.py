import pytest

from agents.pricing_agent import PricingAgent


# Instantiate agent
pricing_agent = PricingAgent()


# ==================================================
# Test Case 1:
# Strong Credit + Good Income → APPROVED
# ==================================================

def test_pricing_approved(monkeypatch):

    # Mock Credit API Response
    class MockCreditResponse:

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "credit_score": 780
            }

    # Mock Bank API Response
    class MockBankResponse:

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "monthly_income": 100000,
                "existing_emi": 20000
            }

    # Mock requests.post
    def mock_post(url, json):

        if "credit-score" in url:
            return MockCreditResponse()

        elif "bank-statements" in url:
            return MockBankResponse()

    monkeypatch.setattr(
        "requests.post",
        mock_post
    )

    result = pricing_agent.calculate_loan_pricing(
        customer_id="C001"
    )

    assert result["pricing_status"] == "APPROVED"

    assert result["interest_rate"] == 11.5

    assert result["eligible_loan_amount"] > 0


# ==================================================
# Test Case 2:
# Low Credit Score → REJECTED
# ==================================================

def test_pricing_low_credit(monkeypatch):

    class MockCreditResponse:

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "credit_score": 620
            }

    class MockBankResponse:

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "monthly_income": 80000,
                "existing_emi": 10000
            }

    def mock_post(url, json):

        if "credit-score" in url:
            return MockCreditResponse()

        elif "bank-statements" in url:
            return MockBankResponse()

    monkeypatch.setattr(
        "requests.post",
        mock_post
    )

    result = pricing_agent.calculate_loan_pricing(
        customer_id="C002"
    )

    assert result["pricing_status"] == "REJECTED"

    assert result["remarks"] == (
        "Credit score too low"
    )


# ==================================================
# Test Case 3:
# High EMI Burden → REJECTED
# ==================================================

def test_pricing_high_emi(monkeypatch):

    class MockCreditResponse:

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "credit_score": 750
            }

    class MockBankResponse:

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "monthly_income": 50000,
                "existing_emi": 35000
            }

    def mock_post(url, json):

        if "credit-score" in url:
            return MockCreditResponse()

        elif "bank-statements" in url:
            return MockBankResponse()

    monkeypatch.setattr(
        "requests.post",
        mock_post
    )

    result = pricing_agent.calculate_loan_pricing(
        customer_id="C003"
    )

    assert result["pricing_status"] == "REJECTED"

    assert result["remarks"] == (
        "Existing EMI burden too high"
    )


# ==================================================
# Test Case 4:
# Missing Credit Score → FAILED
# ==================================================

def test_pricing_missing_credit_score(monkeypatch):

    class MockCreditResponse:

        def raise_for_status(self):
            pass

        def json(self):
            return {}

    class MockBankResponse:

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "monthly_income": 70000,
                "existing_emi": 10000
            }

    def mock_post(url, json):

        if "credit-score" in url:
            return MockCreditResponse()

        elif "bank-statements" in url:
            return MockBankResponse()

    monkeypatch.setattr(
        "requests.post",
        mock_post
    )

    result = pricing_agent.calculate_loan_pricing(
        customer_id="C004"
    )

    assert result["pricing_status"] == "FAILED"

    assert result["remarks"] == (
        "Credit score unavailable"
    )


# ==================================================
# Test Case 5:
# Missing Income Data → FAILED
# ==================================================

def test_pricing_missing_income(monkeypatch):

    class MockCreditResponse:

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "credit_score": 760
            }

    class MockBankResponse:

        def raise_for_status(self):
            pass

        def json(self):
            return {}

    def mock_post(url, json):

        if "credit-score" in url:
            return MockCreditResponse()

        elif "bank-statements" in url:
            return MockBankResponse()

    monkeypatch.setattr(
        "requests.post",
        mock_post
    )

    result = pricing_agent.calculate_loan_pricing(
        customer_id="C005"
    )

    assert result["pricing_status"] == "FAILED"

    assert result["remarks"] == (
        "Income details unavailable"
    )


# ==================================================
# Test Case 6:
# Insufficient Repayment Capacity → REJECTED
# ==================================================

def test_pricing_insufficient_capacity(monkeypatch):

    class MockCreditResponse:

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "credit_score": 720
            }

    class MockBankResponse:

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "monthly_income": 40000,
                "existing_emi": 25000
            }

    def mock_post(url, json):

        if "credit-score" in url:
            return MockCreditResponse()

        elif "bank-statements" in url:
            return MockBankResponse()

    monkeypatch.setattr(
        "requests.post",
        mock_post
    )

    result = pricing_agent.calculate_loan_pricing(
        customer_id="C006"
    )

    assert result["pricing_status"] == "REJECTED"

    assert result["remarks"] == (
        "Insufficient repayment capacity"
    )


# ==================================================
# Test Case 7:
# Premium Credit Score → Lowest Interest Rate
# ==================================================

def test_pricing_best_interest_rate(monkeypatch):

    class MockCreditResponse:

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "credit_score": 820
            }

    class MockBankResponse:

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "monthly_income": 150000,
                "existing_emi": 30000
            }

    def mock_post(url, json):

        if "credit-score" in url:
            return MockCreditResponse()

        elif "bank-statements" in url:
            return MockBankResponse()

    monkeypatch.setattr(
        "requests.post",
        mock_post
    )

    result = pricing_agent.calculate_loan_pricing(
        customer_id="C007"
    )

    assert result["pricing_status"] == "APPROVED"

    assert result["interest_rate"] == 10.5