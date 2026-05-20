import pytest
from unittest.mock import patch, Mock

from agents.compliance_agent import ComplianceAgent


# Instantiate agent
compliance_agent = ComplianceAgent()


# Helper function to create mock response
def mock_response(json_data, status_code=200):
    mock_resp = Mock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data
    mock_resp.raise_for_status.return_value = None
    return mock_resp


# ================================
# Test Case 1: All Checks Pass
# ================================
@patch("agents.compliance_agent.requests.post")
def test_compliance_success(mock_post):

    mock_post.side_effect = [
        mock_response({
            "kyc_status": "VERIFIED",
            "blacklisted": False
        }),
        mock_response({
            "credit_score": 750
        })
    ]

    result = compliance_agent.verify_compliance("C001")

    assert result["compliance_status"] == "APPROVED"
    assert result["credit_score"] == 750


# ================================
# Test Case 2: KYC Failed
# ================================
@patch("agents.compliance_agent.requests.post")
def test_compliance_kyc_failed(mock_post):

    mock_post.side_effect = [
        mock_response({
            "kyc_status": "FAILED",
            "blacklisted": False
        }),
        mock_response({
            "credit_score": 750
        })
    ]

    result = compliance_agent.verify_compliance("C002")

    assert result["compliance_status"] == "FAILED"
    assert result["remarks"] == "KYC verification failed"


# ================================
# Test Case 3: Blacklisted Customer
# ================================
@patch("agents.compliance_agent.requests.post")
def test_compliance_blacklisted(mock_post):

    mock_post.side_effect = [
        mock_response({
            "kyc_status": "VERIFIED",
            "blacklisted": True
        }),
        mock_response({
            "credit_score": 750
        })
    ]

    result = compliance_agent.verify_compliance("C003")

    assert result["compliance_status"] == "FAILED"
    assert result["remarks"] == "Customer is blacklisted"


# ================================
# Test Case 4: Low Credit Score
# ================================
@patch("agents.compliance_agent.requests.post")
def test_compliance_low_credit_score(mock_post):

    mock_post.side_effect = [
        mock_response({
            "kyc_status": "VERIFIED",
            "blacklisted": False
        }),
        mock_response({
            "credit_score": 600
        })
    ]

    result = compliance_agent.verify_compliance("C004")

    assert result["compliance_status"] == "FAILED"
    assert result["remarks"] == "Low credit score"


# ================================
# Test Case 5: API Failure
# ================================
@patch("agents.compliance_agent.requests.post")
def test_compliance_api_failure(mock_post):

    mock_post.side_effect = Exception("API Down")

    result = compliance_agent.verify_compliance("C005")

    assert result["compliance_status"] == "FAILED"
    assert "External API error" in result["remarks"]