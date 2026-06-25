from autogen_agentchat.agents import UserProxyAgent
import requests
import uuid
from datetime import datetime, timedelta

DISBURSEMENT_API_URL = "http://localhost:8002/disbursement/process"


class DisbursementAgent(UserProxyAgent):
    """
    Disbursement Agent
    Handles loan disbursement to customer bank account
    """

    def __init__(self):
        super().__init__(name="Disbursement_Agent")

    def process_disbursement(
        self,
        customer_id: str,
        customer_name: str,
        loan_amount: float,
        sanction_id: str,
        signature_id: str
    ) -> dict:
        """
        Process loan disbursement to customer account
        """
        try:
            response = requests.post(
                DISBURSEMENT_API_URL,
                json={
                    "customer_id": customer_id,
                    "customer_name": customer_name,
                    "loan_amount": loan_amount,
                    "sanction_id": sanction_id,
                    "signature_id": signature_id
                },
                timeout=15
            )
            response.raise_for_status()
            disburse_data = response.json()

            if disburse_data.get("disbursement_status") == "SUCCESS":
                return {
                    "disbursement_status": "SUCCESS",
                    "disbursement_id": disburse_data.get("disbursement_id"),
                    "amount_disbursed": disburse_data.get("amount_disbursed"),
                    "processing_time": disburse_data.get("processing_time"),
                    "bank_reference": disburse_data.get("bank_reference"),
                    "expected_credit_date": disburse_data.get("expected_credit_date"),
                    "remarks": disburse_data.get("message", "Loan disbursed successfully")
                }

            return {
                "disbursement_status": "FAILED",
                "disbursement_id": None,
                "amount_disbursed": 0,
                "processing_time": None,
                "bank_reference": None,
                "expected_credit_date": None,
                "remarks": disburse_data.get("message", "Disbursement processing failed")
            }

        except requests.exceptions.RequestException as e:
            return {
                "disbursement_status": "FAILED",
                "disbursement_id": None,
                "amount_disbursed": 0,
                "processing_time": None,
                "bank_reference": None,
                "expected_credit_date": None,
                "remarks": f"Disbursement API error: {str(e)}"
            }
        except Exception as e:
            return {
                "disbursement_status": "FAILED",
                "disbursement_id": None,
                "amount_disbursed": 0,
                "processing_time": None,
                "bank_reference": None,
                "expected_credit_date": None,
                "remarks": f"Unexpected error: {str(e)}"
            }


# Instantiate agent
disbursement_agent = DisbursementAgent()


def disbursement_agent_task(
    customer_id: str,
    customer_name: str,
    loan_amount: float,
    sanction_id: str,
    signature_id: str
) -> dict:
    """
    Task function for Master Agent
    Process loan disbursement
    """
    return disbursement_agent.process_disbursement(
        customer_id=customer_id,
        customer_name=customer_name,
        loan_amount=loan_amount,
        sanction_id=sanction_id,
        signature_id=signature_id
    )
