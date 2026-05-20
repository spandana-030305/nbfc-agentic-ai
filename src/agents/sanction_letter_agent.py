from autogen_agentchat.agents import UserProxyAgent
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet

import uuid
import os


# ---------------------------------------------------
# SANCTION LETTER AGENT
# ---------------------------------------------------

class SanctionLetterAgent(UserProxyAgent):

    def __init__(self):
        super().__init__(name="Sanction_Letter_Agent")

    def generate_sanction_letter(
        self,
        customer_id: str,
        customer_name: str,
        loan_amount: float,
        interest_rate: float,
        tenure_months: int,
        underwriting_decision: str,
        pricing_status: str
    ):
        """
        Generates a loan sanction letter PDF
        after underwriting and pricing approval.
        """

        # ---------------------------------------------------
        # VALIDATIONS
        # ---------------------------------------------------

        if underwriting_decision != "APPROVED":

            return {
                "sanction_status": "FAILED",
                "remarks":
                    "Loan not approved by underwriting"
            }

        if pricing_status != "APPROVED":

            return {
                "sanction_status": "FAILED",
                "remarks":
                    "Pricing approval not available"
            }

        # ---------------------------------------------------
        # SANCTION DETAILS
        # ---------------------------------------------------

        sanction_id = (
            f"SAN-{uuid.uuid4().hex[:8].upper()}"
        )

        sanction_date = datetime.now().strftime(
            "%Y-%m-%d"
        )

        # ---------------------------------------------------
        # EMI CALCULATION
        # ---------------------------------------------------

        monthly_interest = (
            interest_rate / 12 / 100
        )

        estimated_emi = (
            loan_amount *
            monthly_interest *
            ((1 + monthly_interest) ** tenure_months)
        ) / (
            ((1 + monthly_interest) ** tenure_months)
            - 1
        )

        # ---------------------------------------------------
        # SANCTION LETTER CONTENT
        # ---------------------------------------------------

        sanction_letter = f"""
LOAN SANCTION LETTER

Sanction ID      : {sanction_id}
Date             : {sanction_date}

Customer ID      : {customer_id}
Customer Name    : {customer_name}

--------------------------------------------------

LOAN DETAILS

Approved Loan Amount : ₹{loan_amount:,.2f}

Interest Rate        : {interest_rate}%

Loan Tenure          : {tenure_months} months

Estimated EMI        : ₹{estimated_emi:,.2f}

--------------------------------------------------

TERMS AND CONDITIONS

1. Loan approval is subject to final document verification.

2. EMI must be paid on or before the due date.

3. Delayed payments may attract penalty charges.

4. Bank/NBFC reserves the right to revoke the sanction
   if fraudulent information is detected.

5. Customer must complete eSign verification before
   disbursement.

--------------------------------------------------

STATUS

Loan Status : SANCTIONED

--------------------------------------------------

Thank you for choosing our NBFC services.
"""

        # ---------------------------------------------------
        # CREATE PDF DIRECTORY
        # ---------------------------------------------------

        os.makedirs(
            "generated_sanction_letters",
            exist_ok=True
        )

        pdf_path = (
            f"generated_sanction_letters/"
            f"{sanction_id}.pdf"
        )

        # ---------------------------------------------------
        # GENERATE PDF
        # ---------------------------------------------------

        document = SimpleDocTemplate(
            pdf_path
        )

        styles = getSampleStyleSheet()

        pdf_content = []

        pdf_content.append(
            Paragraph(
                "LOAN SANCTION LETTER",
                styles["Title"]
            )
        )

        pdf_content.append(
            Spacer(1, 12)
        )

        for line in sanction_letter.split("\n"):

            if line.strip():

                pdf_content.append(
                    Paragraph(
                        line,
                        styles["BodyText"]
                    )
                )

        document.build(pdf_content)

        # ---------------------------------------------------
        # RESPONSE
        # ---------------------------------------------------

        return {

            "sanction_status": "APPROVED",

            "sanction_id": sanction_id,

            "customer_id": customer_id,

            "customer_name": customer_name,

            "loan_amount": loan_amount,

            "interest_rate": interest_rate,

            "tenure_months": tenure_months,

            "estimated_emi": round(
                estimated_emi,
                2
            ),

            "generated_on": sanction_date,

            "pdf_path": pdf_path,

            "sanction_letter": sanction_letter,

            "remarks":
                "Sanction letter PDF generated successfully"
        }


# ---------------------------------------------------
# INSTANTIATE AGENT
# ---------------------------------------------------

sanction_letter_agent = SanctionLetterAgent()


# ---------------------------------------------------
# TASK FUNCTION FOR MASTER AGENT
# ---------------------------------------------------

def sanction_letter_agent_task(
    customer_id: str,
    customer_name: str,
    loan_amount: float,
    interest_rate: float,
    tenure_months: int,
    underwriting_decision: str,
    pricing_status: str
):
    """
    Task function for Master Agent
    """

    return sanction_letter_agent.generate_sanction_letter(
        customer_id=customer_id,
        customer_name=customer_name,
        loan_amount=loan_amount,
        interest_rate=interest_rate,
        tenure_months=tenure_months,
        underwriting_decision=underwriting_decision,
        pricing_status=pricing_status
    )