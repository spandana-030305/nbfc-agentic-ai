from autogen_agentchat.agents import UserProxyAgent
import requests

BANK_API_URL = "http://localhost:8002/bank-statements"

class IncomeVerificationAgent(UserProxyAgent):
    def __init__(self):
        super().__init__(name = "Income_Verification_Agent")

    def verify_income(self, customer_id: str):
        """
        Calls Bank Statement api and verifies income eligibility
        """
        response = requests.post(
            "http://localhost:8002/bank-statements/fetch",
            json={"customer_id": customer_id}
        )
        
        response.raise_for_status()
        record = response.json()

        monthly_income=record["monthly_income"]
        emi_amount = record["emi_amount"]
        avg_balance = record["avg_balance"]

        # Prevent division by zero
        if monthly_income <= 0:
            return {
                "income_status": "FAILED",
                "emi_ratio": None,
                "remarks": "Monthly income is 0 or invalid, cannot verify income"
            }

        emi_ratio = emi_amount / monthly_income

        # Business rules
        if emi_ratio > 0.4:
            return {
                "income_status": "FAILED",
                "emi_ratio": round(emi_ratio, 2),
                "remarks": "High EMI burden"
            }

        if avg_balance < 10000:
            return {
                "income_status": "FAILED",
                "emi_ratio": round(emi_ratio, 2),
                "remarks": "Low average balance"
            }

        return {
            "income_status": "VERIFIED",
            "monthly_income": monthly_income,
            "emi_ratio": round(emi_ratio, 2),
            "remarks": "Income stable and eligible"
        }

# Instantiate agent
income_agent = IncomeVerificationAgent()

def income_agent_task(customer_id: str):
    """
    Task function for Master Agent
    """
    return income_agent.verify_income(customer_id)