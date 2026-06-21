from autogen_agentchat.agents import UserProxyAgent
import requests

CREDIT_BUREAU_API = "http://localhost:8002/credit-score"


class UnderwritingAgent(UserProxyAgent):

    def __init__(self):
        super().__init__(name="Underwriting_Agent")

    def evaluate_application(
        self,
        customer_id: str,
        requested_loan_amount: float,
        preapproved_limit: float,
        monthly_salary: float | None = None,
        expected_emi: float | None = None
    ):
        """
        Underwriting Rules

        1. Fetch credit score
        2. Reject if credit score < 700

        3. If requested amount <= pre-approved limit
           -> APPROVED

        4. If requested amount <= 2x pre-approved limit
           -> Require salary verification
           -> Approve only if EMI <= 50% salary

        5. Reject if amount > 2x pre-approved limit
        """

        # -----------------------------------
        # FETCH CREDIT SCORE
        # -----------------------------------

        try:

            response = requests.post(
                CREDIT_BUREAU_API,
                json={
                    "customer_id": customer_id
                }
            )

            response.raise_for_status()

            credit_data = response.json()

            credit_score = credit_data.get(
                "credit_score",
                0
            )

        except Exception as e:

            return {
                "decision": "REJECTED",
                "remarks": f"Credit bureau error: {str(e)}"
            }

        # -----------------------------------
        # RULE 1
        # CREDIT SCORE
        # -----------------------------------

        if credit_score < 700:

            return {
                "decision": "REJECTED",
                "credit_score": credit_score,
                "remarks": "Credit score below minimum threshold"
            }

        # -----------------------------------
        # RULE 2
        # INSTANT APPROVAL
        # -----------------------------------

        if requested_loan_amount <= preapproved_limit:

            return {
                "decision": "APPROVED",
                "credit_score": credit_score,
                "remarks": "Within pre-approved limit"
            }

        # -----------------------------------
        # RULE 3
        # SALARY SLIP REQUIRED
        # -----------------------------------

        if requested_loan_amount <= (
            2 * preapproved_limit
        ):

            if monthly_salary is None:

                return {
                    "decision": "PENDING_DOCUMENT",
                    "credit_score": credit_score,
                    "remarks": "Salary slip required"
                }

            if expected_emi is None:

                return {
                    "decision": "REJECTED",
                    "credit_score": credit_score,
                    "remarks": "Expected EMI missing"
                }

            if expected_emi <= (
                monthly_salary * 0.50
            ):

                return {
                    "decision": "APPROVED",
                    "credit_score": credit_score,
                    "remarks":
                    "Approved after salary verification"
                }

            return {
                "decision": "REJECTED",
                "credit_score": credit_score,
                "remarks":
                "EMI exceeds 50% of salary"
            }

        # -----------------------------------
        # RULE 4
        # EXCEEDS 2X LIMIT
        # -----------------------------------

        return {
            "decision": "REJECTED",
            "credit_score": credit_score,
            "remarks":
            "Requested amount exceeds underwriting limit"
        }


underwriting_agent = UnderwritingAgent()


def underwriting_agent_task(
    customer_id: str,
    requested_loan_amount: float,
    preapproved_limit: float,
    monthly_salary: float | None = None,
    expected_emi: float | None = None
):

    return underwriting_agent.evaluate_application(
        customer_id=customer_id,
        requested_loan_amount=requested_loan_amount,
        preapproved_limit=preapproved_limit,
        monthly_salary=monthly_salary,
        expected_emi=expected_emi
    )