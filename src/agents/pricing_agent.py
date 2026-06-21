from autogen_agentchat.agents import UserProxyAgent
import requests

# ---------------------------------------------------
# EXTERNAL API CONFIGURATION
# ---------------------------------------------------

CIBIL_API_URL = "http://localhost:8002/credit-score"
BANK_API_URL = "http://localhost:8002/bank-statements"


# ---------------------------------------------------
# PRICING AGENT
# ---------------------------------------------------

class PricingAgent(UserProxyAgent):

    def __init__(self):
        super().__init__(name="Pricing_Agent")

    def calculate_loan_pricing(self, customer_id: str):
        """
        Calculates:
        - Eligible loan amount
        - Interest rate
        - Recommended tenure
        - EMI burden analysis

        Based on:
        - Credit score
        - Monthly income
        - Existing liabilities
        """

        try:

            # ----------------------------------------
            # FETCH CREDIT SCORE
            # ----------------------------------------

            credit_response = requests.post(
                CIBIL_API_URL,
                json={"customer_id": customer_id}
            )

            credit_response.raise_for_status()

            credit_data = credit_response.json()

            # ----------------------------------------
            # FETCH BANK STATEMENTS / INCOME DATA
            # ----------------------------------------

            bank_response = requests.post(
                BANK_API_URL,
                json={"customer_id": customer_id}
            )

            bank_response.raise_for_status()

            bank_data = bank_response.json()

        except requests.exceptions.RequestException as e:

            return {
                "pricing_status": "FAILED",
                "remarks": f"External API error: {str(e)}"
            }

        # ---------------------------------------------------
        # EXTRACT REQUIRED DATA
        # ---------------------------------------------------

        credit_score = credit_data.get("credit_score")

        monthly_income = bank_data.get("monthly_income")

        existing_emi = bank_data.get("existing_emi", 0)

        # ---------------------------------------------------
        # VALIDATIONS
        # ---------------------------------------------------

        if credit_score is None:

            return {
                "pricing_status": "FAILED",
                "remarks": "Credit score unavailable"
            }

        if monthly_income is None:

            return {
                "pricing_status": "FAILED",
                "remarks": "Income details unavailable"
            }

        # ---------------------------------------------------
        # EMI RATIO CALCULATION
        # ---------------------------------------------------

        emi_ratio = existing_emi / monthly_income

        # ---------------------------------------------------
        # EMI BURDEN CHECK
        # ---------------------------------------------------

        if emi_ratio > 0.6:

            return {
                "pricing_status": "REJECTED",
                "remarks": "Existing EMI burden too high",
                "emi_ratio": round(emi_ratio, 2)
            }

        # ---------------------------------------------------
        # INTEREST RATE LOGIC
        # ---------------------------------------------------

        if credit_score >= 800:
            interest_rate = 10.5

        elif credit_score >= 750:
            interest_rate = 11.5

        elif credit_score >= 700:
            interest_rate = 12.5

        elif credit_score >= 650:
            interest_rate = 14.0

        else:
            return {
                "pricing_status": "REJECTED",
                "remarks": "Credit score too low"
            }

        # ---------------------------------------------------
        # ELIGIBLE EMI CALCULATION
        # ---------------------------------------------------

        # Rule:
        # Max 50% salary can go towards EMI

        eligible_emi = (monthly_income * 0.5) - existing_emi

        if eligible_emi <= 0:

            return {
                "pricing_status": "REJECTED",
                "remarks": "Insufficient repayment capacity"
            }

        # ---------------------------------------------------
        # TENURE DECISION
        # ---------------------------------------------------

        if credit_score >= 750:
            tenure_months = 84

        elif credit_score >= 700:
            tenure_months = 60

        else:
            tenure_months = 36

        # ---------------------------------------------------
        # ELIGIBLE LOAN AMOUNT
        # ---------------------------------------------------

        eligible_loan_amount = eligible_emi * tenure_months

        # ---------------------------------------------------
        # ESTIMATED EMI
        # ---------------------------------------------------

        estimated_emi = eligible_loan_amount / tenure_months

        # ---------------------------------------------------
        # FINAL RESPONSE
        # ---------------------------------------------------

        return {

            "pricing_status": "APPROVED",

            "customer_id": customer_id,

            "credit_score": credit_score,

            "monthly_income": monthly_income,

            "existing_emi": existing_emi,

            "emi_ratio": round(emi_ratio, 2),

            "interest_rate": interest_rate,

            "eligible_emi": round(eligible_emi, 2),

            "eligible_loan_amount": round(
                eligible_loan_amount,
                2
            ),

            "recommended_tenure_months": tenure_months,

            "estimated_monthly_emi": round(
                estimated_emi,
                2
            ),

            "remarks": "Loan pricing calculated successfully"
        }


# ---------------------------------------------------
# INSTANTIATE AGENT
# ---------------------------------------------------

pricing_agent = PricingAgent()


# ---------------------------------------------------
# TASK FUNCTION FOR MASTER AGENT
# ---------------------------------------------------

def pricing_agent_task(customer_id: str):
    """
    Task function for Master Agent
    """

    return pricing_agent.calculate_loan_pricing(
        customer_id
    )