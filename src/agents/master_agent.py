from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

# -----------------------------
# TOOLS
# -----------------------------

@tool
def kyc_agent_tool(pan: str, name: str, dob: str) -> str:
    """
    Perform PAN-based KYC verification.
    """

    from agents.kyc_agent import kyc_agent_task

    result = kyc_agent_task(
        pan=pan,
        name=name,
        dob=dob
    )

    return f"KYC Result: {result}"


@tool
def income_agent_tool(customer_id: str) -> str:
    """
    Perform income verification using bank statements.
    """

    from agents.income_agent import income_agent_task

    result = income_agent_task(customer_id)

    return f"Income Verification Result: {result}"


@tool
def sales_agent_tool(customer_id: str) -> str:
    """
    Get best loan offers for customer ID.
    """

    from agents.sales_agent import sales_agent_task

    offers = sales_agent_task(customer_id)

    return f"Found offers: {offers}"


@tool
def compliance_agent_tool(customer_id: str) -> str:
    """
    Perform compliance verification using:
    - KYC status
    - Blacklist check
    - Credit score validation
    """

    from agents.compliance_agent import compliance_agent_task

    result = compliance_agent_task(customer_id)

    return f"Compliance Verification Result: {result}"


@tool
def underwriting_agent_tool(
    customer_id: str,
    credit_score: int,
    income_status: str,
    emi_ratio: float
) -> str:
    """
    Perform underwriting evaluation for loan approval.
    """

    from agents.underwriting_agent import underwriting_agent_task

    result = underwriting_agent_task(
        customer_id=customer_id,
        credit_score=credit_score,
        income_status=income_status,
        emi_ratio=emi_ratio
    )

    return f"Underwriting Result: {result}"


@tool
def pricing_agent_tool(customer_id: str) -> str:
    """
    Calculate loan pricing details:
    - Eligible loan amount
    - Interest rate
    - EMI eligibility
    - Recommended tenure
    """

    from agents.pricing_agent import pricing_agent_task

    result = pricing_agent_task(customer_id)

    return f"Pricing Result: {result}"


@tool
def sanction_letter_agent_tool(
    customer_id: str,
    customer_name: str,
    loan_amount: float,
    interest_rate: float,
    tenure_months: int,
    underwriting_decision: str,
    pricing_status: str
) -> str:
    """
    Generate loan sanction letter.
    """

    from agents.sanction_letter_agent import (
        sanction_letter_agent_task
    )

    result = sanction_letter_agent_task(
        customer_id=customer_id,
        customer_name=customer_name,
        loan_amount=loan_amount,
        interest_rate=interest_rate,
        tenure_months=tenure_months,
        underwriting_decision=underwriting_decision,
        pricing_status=pricing_status
    )

    return f"Sanction Letter Result: {result}"


# -----------------------------
# MASTER AGENT
# -----------------------------

class MasterAgent:

    def __init__(self):

        self.llm = ChatOllama(
            model="llama3.1:8b",
            temperature=0.1,
            base_url="http://localhost:11434",
        )

        # -----------------------------
        # STATUS TRACKING
        # -----------------------------

        self.kyc_status = None
        self.income_status = None
        self.compliance_status = None
        self.underwriting_decision = None
        self.pricing_status = None
        self.sanction_status = None

        # -----------------------------
        # REGISTER ALL TOOLS
        # -----------------------------

        tools = [
            kyc_agent_tool,
            income_agent_tool,
            sales_agent_tool,
            compliance_agent_tool,
            underwriting_agent_tool,
            pricing_agent_tool,
            sanction_letter_agent_tool
        ]

        # -----------------------------
        # MEMORY
        # -----------------------------

        checkpointer = MemorySaver()

        # -----------------------------
        # CREATE AGENT
        # -----------------------------

        self.agent = create_agent(
            self.llm,
            tools,
            checkpointer=checkpointer
        )

    # -----------------------------
    # RUN MASTER AGENT
    # -----------------------------

    def run(self, user_message: str) -> str:

        config = {
            "configurable": {
                "thread_id": "1"
            }
        }

        result = self.agent.invoke(
            {
                "messages": [
                    ("user", user_message)
                ]
            },
            config
        )

        # -----------------------------
        # PARSE AGENT RESPONSES
        # -----------------------------

        for msg in result["messages"]:

            if isinstance(msg.content, str):
                print("AGENT MSG:", msg.content)

            # -----------------------------
            # KYC STATUS
            # -----------------------------

            if "KYC Result" in msg.content:

                if "'kyc_status': 'VERIFIED'" in msg.content:
                    self.kyc_status = "VERIFIED"

                elif "'kyc_status': 'FAILED'" in msg.content:
                    self.kyc_status = "FAILED"

            # -----------------------------
            # INCOME STATUS
            # -----------------------------

            if "Income Verification Result" in msg.content:

                if "'income_status': 'VERIFIED'" in msg.content:
                    self.income_status = "VERIFIED"

                elif "'income_status': 'FAILED'" in msg.content:
                    self.income_status = "FAILED"

            # -----------------------------
            # COMPLIANCE STATUS
            # -----------------------------

            if "Compliance Verification Result" in msg.content:

                if "'compliance_status': 'APPROVED'" in msg.content:
                    self.compliance_status = "APPROVED"

                elif "'compliance_status': 'FAILED'" in msg.content:
                    self.compliance_status = "FAILED"

            # -----------------------------
            # UNDERWRITING DECISION
            # -----------------------------

            if "Underwriting Result" in msg.content:

                if "'decision': 'APPROVED'" in msg.content:
                    self.underwriting_decision = "APPROVED"

                elif "'decision': 'REJECTED'" in msg.content:
                    self.underwriting_decision = "REJECTED"

                elif "'decision': 'REVIEW'" in msg.content:
                    self.underwriting_decision = "REVIEW"

            # -----------------------------
            # PRICING STATUS
            # -----------------------------

            if "Pricing Result" in msg.content:

                if "'pricing_status': 'APPROVED'" in msg.content:
                    self.pricing_status = "APPROVED"

                elif "'pricing_status': 'FAILED'" in msg.content:
                    self.pricing_status = "FAILED"

                elif "'pricing_status': 'REJECTED'" in msg.content:
                    self.pricing_status = "REJECTED"

            # -----------------------------
            # SANCTION LETTER STATUS
            # -----------------------------

            if "Sanction Letter Result" in msg.content:

                if "'sanction_status': 'APPROVED'" in msg.content:
                    self.sanction_status = "APPROVED"

                elif "'sanction_status': 'FAILED'" in msg.content:
                    self.sanction_status = "FAILED"

        # -----------------------------
        # HARD COMPLIANCE GATES
        # -----------------------------

        if "loan" in user_message.lower():

            # KYC Check
            if self.kyc_status == "FAILED":
                return (
                    "Loan cannot be processed because "
                    "KYC verification failed."
                )

            # Income Check
            if self.income_status == "FAILED":
                return (
                    "Loan cannot be processed because "
                    "income eligibility failed."
                )

            # Compliance Check
            if self.compliance_status == "FAILED":
                return (
                    "Loan cannot be processed because "
                    "compliance verification failed."
                )

            # Underwriting Check
            if self.underwriting_decision == "REJECTED":
                return (
                    "Loan application rejected during "
                    "underwriting evaluation."
                )

            # Manual Review
            if self.underwriting_decision == "REVIEW":
                return (
                    "Loan application requires manual review "
                    "by underwriting team."
                )

            # Pricing Check
            if self.pricing_status == "REJECTED":

                return (
                    "Loan pricing rejected due to "
                    "eligibility or EMI burden."
                )

            # Sanction Letter Check
            if self.sanction_status == "FAILED":

                return (
                    "Loan sanction letter generation failed."
                )

        # -----------------------------
        # FINAL RESPONSE
        # -----------------------------

        return result["messages"][-1].content


# -----------------------------
# MAIN EXECUTION
# -----------------------------

if __name__ == "__main__":

    master_agent = MasterAgent()

    print("\n===== AI LOAN PROCESSING SYSTEM =====\n")

    while True:

        user_input = input("User: ")

        if user_input.lower() in ["exit", "quit"]:

            print("Exiting system...")
            break

        response = master_agent.run(user_input)

        print("\nMASTER AGENT RESPONSE:")
        print(response)
        print()