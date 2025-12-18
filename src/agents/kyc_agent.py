from autogen_agentchat.agents import UserProxyAgent
import requests

PAN_API_URL = "http://127.0.0.1:8000/pan/verify"


class KYCAgent(UserProxyAgent):
    def __init__(self):
        super().__init__(name="KYC_Agent")

    def verify_pan_kyc(self, pan: str, name: str, dob: str):
        """
        Calls PAN verification API and returns KYC result
        """
        payload = {
            "pan": pan,
            "name": name,
            "dob": dob
        }

        response = requests.post(PAN_API_URL, json=payload, timeout=5)
        response.raise_for_status()
        pan_result = response.json()

        # Normalize response for Master Agent
        if pan_result.get("status") == "VERIFIED":
            return {
                "kyc_status": "VERIFIED",
                "pan_status": "VERIFIED",
                "remarks": pan_result.get("message")
            }

        return {
            "kyc_status": "FAILED",
            "pan_status": "FAILED",
            "remarks": pan_result.get("message")
        }


# Instantiate agent
kyc_agent = KYCAgent()

# Optional safety configs (version dependent)
# kyc_agent.human_input_mode = "NEVER"
# kyc_agent.code_execution_enabled = False


# ----------------------------
# Simple callable task
# ----------------------------
def kyc_agent_task(pan: str, name: str, dob: str):
    """
    Task function used by Master Agent
    """
    return kyc_agent.verify_pan_kyc(pan, name, dob)

