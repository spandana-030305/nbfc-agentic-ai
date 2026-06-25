from autogen_agentchat.agents import UserProxyAgent
import requests
import uuid
from datetime import datetime

ESIGN_API_URL = "http://localhost:8002/esign/sign"


class eSignAgent(UserProxyAgent):
    """
    eSign Agent
    Handles digital signature of loan documents
    """

    def __init__(self):
        super().__init__(name="eSign_Agent")

    def sign_documents(
        self,
        customer_id: str,
        customer_name: str,
        loan_amount: float,
        sanction_id: str
    ) -> dict:
        """
        Get customer digital signature for loan documents
        """
        try:
            response = requests.post(
                ESIGN_API_URL,
                json={
                    "customer_id": customer_id,
                    "customer_name": customer_name,
                    "loan_amount": loan_amount,
                    "sanction_id": sanction_id
                },
                timeout=10
            )
            response.raise_for_status()
            esign_data = response.json()

            if esign_data.get("sign_status") == "SIGNED":
                return {
                    "esign_status": "SIGNED",
                    "signature_id": esign_data.get("signature_id"),
                    "signed_at": esign_data.get("signed_at"),
                    "documents": esign_data.get("documents", []),
                    "remarks": esign_data.get("message", "Documents signed successfully")
                }

            return {
                "esign_status": "FAILED",
                "signature_id": None,
                "signed_at": None,
                "documents": [],
                "remarks": esign_data.get("message", "Document signing failed")
            }

        except requests.exceptions.RequestException as e:
            return {
                "esign_status": "FAILED",
                "signature_id": None,
                "signed_at": None,
                "documents": [],
                "remarks": f"eSign API error: {str(e)}"
            }
        except Exception as e:
            return {
                "esign_status": "FAILED",
                "signature_id": None,
                "signed_at": None,
                "documents": [],
                "remarks": f"Unexpected error: {str(e)}"
            }


# Instantiate agent
esign_agent = eSignAgent()


def esign_agent_task(
    customer_id: str,
    customer_name: str,
    loan_amount: float,
    sanction_id: str
) -> dict:
    """
    Task function for Master Agent
    Sign loan documents digitally
    """
    return esign_agent.sign_documents(
        customer_id=customer_id,
        customer_name=customer_name,
        loan_amount=loan_amount,
        sanction_id=sanction_id
    )
