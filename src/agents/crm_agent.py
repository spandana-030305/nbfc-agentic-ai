from autogen_agentchat.agents import UserProxyAgent
import requests

CRM_API_URL = "http://localhost:8002/crm/verify"


class CRMAgent(UserProxyAgent):
    """
    CRM Integration Agent
    Verifies customer phone and address from CRM server
    """

    def __init__(self):
        super().__init__(name="CRM_Agent")

    def verify_crm_details(self, customer_id: str) -> dict:
        """
        Verify phone number and address from CRM system
        Returns verified CRM details for the customer
        """
        try:
            response = requests.post(
                CRM_API_URL,
                json={"customer_id": customer_id},
                timeout=5
            )
            response.raise_for_status()
            crm_data = response.json()

            # Normalize response for Master Agent
            if crm_data.get("crm_verification_status") == "VERIFIED":
                return {
                    "crm_status": "VERIFIED",
                    "phone": crm_data.get("phone"),
                    "address": crm_data.get("address"),
                    "city": crm_data.get("city"),
                    "remarks": crm_data.get("message", "CRM details verified")
                }

            return {
                "crm_status": "FAILED",
                "phone": None,
                "address": None,
                "remarks": crm_data.get("message", "CRM verification failed")
            }

        except requests.exceptions.RequestException as e:
            return {
                "crm_status": "FAILED",
                "phone": None,
                "address": None,
                "remarks": f"CRM API error: {str(e)}"
            }
        except Exception as e:
            return {
                "crm_status": "FAILED",
                "phone": None,
                "address": None,
                "remarks": f"Unexpected error: {str(e)}"
            }


# Instantiate agent
crm_agent = CRMAgent()


def crm_agent_task(customer_id: str) -> dict:
    """
    Task function for Master Agent
    Verify customer CRM details
    """
    return crm_agent.verify_crm_details(customer_id)
