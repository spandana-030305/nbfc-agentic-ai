from autogen_agentchat.agents import UserProxyAgent
import requests

KYC_API_URL = "http://localhost:8002/pan/verify"
CIBIL_API_URL = "http://localhost:8002/credit-score"

class ComplianceAgent(UserProxyAgent):
    def __init__(self):
        super().__init__(name="Compliance_Agent")

    def verify_compliance(self, customer_id: str):
        """
        Calls KYC API and Credit Bureau API
        Applies compliance & eligibility rules
        """

        try:
            # Call KYC API
            kyc_response = requests.post(
                KYC_API_URL,
                json={"customer_id": customer_id}
            )
            kyc_response.raise_for_status()
            kyc_data = kyc_response.json()

            # Call Credit Score API
            credit_response = requests.post(
                CIBIL_API_URL,
                json={"customer_id": customer_id}
            )
            credit_response.raise_for_status()
            credit_data = credit_response.json()

        except requests.exceptions.RequestException as e:
            return {
                "compliance_status": "FAILED",
                "remarks": f"External API error: {str(e)}"
            }

        # Extract required fields
        kyc_status = kyc_data.get("kyc_status")
        is_blacklisted = kyc_data.get("blacklisted", False)
        credit_score = credit_data.get("credit_score")

        # Business Rules

        if kyc_status != "VERIFIED":
            return {
                "compliance_status": "FAILED",
                "credit_score": credit_score,
                "remarks": "KYC verification failed"
            }

        if is_blacklisted:
            return {
                "compliance_status": "FAILED",
                "credit_score": credit_score,
                "remarks": "Customer is blacklisted"
            }

        if credit_score is None or credit_score < 650:
            return {
                "compliance_status": "FAILED",
                "credit_score": credit_score,
                "remarks": "Low credit score"
            }

        # If all checks pass
        return {
            "compliance_status": "APPROVED",
            "credit_score": credit_score,
            "remarks": "Compliance checks passed"
        }


# Instantiate agent
compliance_agent = ComplianceAgent()


def compliance_agent_task(customer_id: str):
    """
    Task function for Master Agent
    """
    return compliance_agent.verify_compliance(customer_id)