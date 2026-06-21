from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver


# ---------------------------------------------------
# TOOLS
# ---------------------------------------------------

@tool
def kyc_agent_tool(
    pan: str,
    name: str,
    dob: str
) -> str:
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
def income_agent_tool(
    customer_id: str
) -> str:
    """
    Perform income verification
    using bank statements.
    """
    from agents.income_agent import income_agent_task

    result = income_agent_task(customer_id)

    return f"Income Verification Result: {result}"


@tool
def sales_agent_tool(
    customer_id: str
) -> str:
    """
    Get best loan offers
    for customer ID.
    """
    from agents.sales_agent import sales_agent_task

    offers = sales_agent_task(customer_id)

    return f"Found offers: {offers}"


@tool
def compliance_agent_tool(
    customer_id: str
) -> str:
    """
    Perform compliance verification.
    """
    from agents.compliance_agent import compliance_agent_task

    result = compliance_agent_task(customer_id)

    return f"Compliance Verification Result: {result}"


@tool
def underwriting_agent_tool(
    customer_id: str,
    requested_loan_amount: float,
    preapproved_limit: float,
    monthly_salary: float = None,
    expected_emi: float = None
) -> str:
    """
    Perform underwriting evaluation.
    """
    from agents.underwriting_agent import underwriting_agent_task

    result = underwriting_agent_task(
        customer_id=customer_id,
        requested_loan_amount=requested_loan_amount,
        preapproved_limit=preapproved_limit,
        monthly_salary=monthly_salary,
        expected_emi=expected_emi
    )

    return f"Underwriting Result: {result}"


@tool
def pricing_agent_tool(
    customer_id: str
) -> str:
    """
    Calculate loan pricing.
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
    Generate sanction letter.
    """
    from agents.sanction_letter_agent import sanction_letter_agent_task

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


# ---------------------------------------------------
# MASTER AGENT
# ---------------------------------------------------

class MasterAgent:

    def __init__(self):

        self.llm = ChatOllama(
            model="llama3.1:8b",
            temperature=0.1,
            base_url="http://localhost:11434"
        )

        # Status tracking
        self.kyc_status = None
        self.income_status = None
        self.compliance_status = None
        self.underwriting_decision = None
        self.pricing_status = None
        self.sanction_status = None

        tools = [
            kyc_agent_tool,
            income_agent_tool,
            sales_agent_tool,
            compliance_agent_tool,
            underwriting_agent_tool,
            pricing_agent_tool,
            sanction_letter_agent_tool
        ]

        checkpointer = MemorySaver()

        self.agent = create_agent(
            self.llm,
            tools,
            checkpointer=checkpointer
        )

    # ---------------------------------------------------
    # RUN MASTER AGENT
    # ---------------------------------------------------

    def run(
        self,
        user_message: str,
        customer_id: str
    ) -> str:

        config = {
            "configurable": {
                "thread_id": "1"
            }
        }

        result = self.agent.invoke(
            {
                "messages": [
                    (
                        "system",
                        f"Customer ID is {customer_id}. "
                        f"Use this ID whenever tools require customer_id."
                    ),
                    ("user", user_message)
                ]
            },
            config
        )

        # ------------------------------------
        # Parse responses
        # ------------------------------------

        for msg in result["messages"]:

            if isinstance(msg.content, str):
                print("AGENT MSG:", msg.content)

            if "KYC Result" in msg.content:
                if "'kyc_status': 'VERIFIED'" in msg.content:
                    self.kyc_status = "VERIFIED"
                elif "'kyc_status': 'FAILED'" in msg.content:
                    self.kyc_status = "FAILED"

            if "Income Verification Result" in msg.content:
                if "'income_status': 'VERIFIED'" in msg.content:
                    self.income_status = "VERIFIED"
                elif "'income_status': 'FAILED'" in msg.content:
                    self.income_status = "FAILED"

            if "Compliance Verification Result" in msg.content:
                if "'compliance_status': 'APPROVED'" in msg.content:
                    self.compliance_status = "APPROVED"
                elif "'compliance_status': 'FAILED'" in msg.content:
                    self.compliance_status = "FAILED"

            if "Underwriting Result" in msg.content:
                if "'decision': 'APPROVED'" in msg.content:
                    self.underwriting_decision = "APPROVED"
                elif "'decision': 'REJECTED'" in msg.content:
                    self.underwriting_decision = "REJECTED"
                elif "'decision': 'PENDING_DOCUMENT'" in msg.content:
                    self.underwriting_decision = "PENDING_DOCUMENT"

            if "Pricing Result" in msg.content:
                if "'pricing_status': 'APPROVED'" in msg.content:
                    self.pricing_status = "APPROVED"
                elif "'pricing_status': 'REJECTED'" in msg.content:
                    self.pricing_status = "REJECTED"

            if "Sanction Letter Result" in msg.content:
                if "'sanction_status': 'APPROVED'" in msg.content:
                    self.sanction_status = "APPROVED"
                elif "'sanction_status': 'FAILED'" in msg.content:
                    self.sanction_status = "FAILED"

        # ------------------------------------
        # Hard gates
        # ------------------------------------

        if "loan" in user_message.lower():

            if self.kyc_status == "FAILED":
                return "Loan cannot be processed because KYC failed."

            if self.income_status == "FAILED":
                return "Loan cannot be processed because income verification failed."

            if self.compliance_status == "FAILED":
                return "Loan cannot be processed because compliance failed."

            if self.underwriting_decision == "REJECTED":
                return "Loan application rejected during underwriting."

            if self.underwriting_decision == "PENDING_DOCUMENT":
                return "Salary slip upload required for underwriting approval."

            if self.pricing_status == "REJECTED":
                return "Loan pricing rejected due to EMI burden or eligibility."

            if self.sanction_status == "FAILED":
                return "Loan sanction letter generation failed."

        return result["messages"][-1].content


# ---------------------------------------------------
# LOCAL TESTING
# ---------------------------------------------------

if __name__ == "__main__":

    master_agent = MasterAgent()

    print("\n===== AI LOAN PROCESSING SYSTEM =====\n")

    while True:

        user_input = input("User: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Exiting system...")
            break

        response = master_agent.run(
            user_message=user_input,
            customer_id="C002"
        )

        print("\nMASTER AGENT RESPONSE:")
        print(response)
        print()