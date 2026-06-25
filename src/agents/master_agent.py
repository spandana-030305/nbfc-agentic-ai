from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from utils.memory import get_shared_memory


# ---------------------------------------------------
# TOOLS - VERIFICATION AGENTS
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
def crm_agent_tool(
    customer_id: str
) -> str:
    """
    Verify customer CRM details (phone, address, city).
    """
    from agents.crm_agent import crm_agent_task

    result = crm_agent_task(customer_id)

    return f"CRM Verification Result: {result}"


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
def compliance_agent_tool(
    customer_id: str
) -> str:
    """
    Perform compliance verification.
    """
    from agents.compliance_agent import compliance_agent_task

    result = compliance_agent_task(customer_id)

    return f"Compliance Verification Result: {result}"


# ---------------------------------------------------
# TOOLS - BUSINESS AGENTS
# ---------------------------------------------------

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


# ---------------------------------------------------
# TOOLS - COMPLETION AGENTS
# ---------------------------------------------------

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


@tool
def esign_agent_tool(
    customer_id: str,
    customer_name: str,
    loan_amount: float,
    sanction_id: str
) -> str:
    """
    Digitally sign loan documents.
    """
    from agents.esign_agent import esign_agent_task

    result = esign_agent_task(
        customer_id=customer_id,
        customer_name=customer_name,
        loan_amount=loan_amount,
        sanction_id=sanction_id
    )

    return f"eSign Result: {result}"


@tool
def disbursement_agent_tool(
    customer_id: str,
    customer_name: str,
    loan_amount: float,
    sanction_id: str,
    signature_id: str
) -> str:
    """
    Process loan disbursement.
    """
    from agents.disbursement_agent import disbursement_agent_task

    result = disbursement_agent_task(
        customer_id=customer_id,
        customer_name=customer_name,
        loan_amount=loan_amount,
        sanction_id=sanction_id,
        signature_id=signature_id
    )

    return f"Disbursement Result: {result}"


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

        # Use shared memory
        self.memory = get_shared_memory()

        # Status tracking
        self.kyc_status = None
        self.crm_status = None
        self.income_status = None
        self.compliance_status = None
        self.underwriting_decision = None
        self.pricing_status = None
        self.sanction_status = None
        self.esign_status = None
        self.disbursement_status = None

        tools = [
            # Verification tools
            kyc_agent_tool,
            crm_agent_tool,
            income_agent_tool,
            compliance_agent_tool,
            # Business logic tools
            sales_agent_tool,
            underwriting_agent_tool,
            pricing_agent_tool,
            # Completion tools
            sanction_letter_agent_tool,
            esign_agent_tool,
            disbursement_agent_tool,
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

        # Store in shared memory
        self.memory.add_message("user", user_message)
        self.memory.set_customer_profile({"customer_id": customer_id})

        config = {
            "configurable": {
                "thread_id": customer_id
            }
        }

        result = self.agent.invoke(
            {
                "messages": [
                    (
                        "system",
                        f"Customer ID is {customer_id}. "
                        f"You are coordinating a loan application process. "
                        f"Current workflow status: {self.memory.get_workflow_state()}"
                    ),
                    ("user", user_message)
                ]
            },
            config
        )

        # ------------------------------------
        # Parse responses and update memory
        # ------------------------------------

        for msg in result["messages"]:

            if isinstance(msg.content, str):
                print("AGENT MSG:", msg.content)

            if "KYC Result" in msg.content:
                if "'kyc_status': 'VERIFIED'" in msg.content:
                    self.kyc_status = "VERIFIED"
                    self.memory.update_workflow_state("kyc_verified", True)
                elif "'kyc_status': 'FAILED'" in msg.content:
                    self.kyc_status = "FAILED"

            if "CRM Verification Result" in msg.content:
                if "'crm_status': 'VERIFIED'" in msg.content:
                    self.crm_status = "VERIFIED"
                    self.memory.update_workflow_state("crm_verified", True)
                elif "'crm_status': 'FAILED'" in msg.content:
                    self.crm_status = "FAILED"

            if "Income Verification Result" in msg.content:
                if "'income_status': 'VERIFIED'" in msg.content:
                    self.income_status = "VERIFIED"
                    self.memory.update_workflow_state("income_verified", True)
                elif "'income_status': 'FAILED'" in msg.content:
                    self.income_status = "FAILED"

            if "Compliance Verification Result" in msg.content:
                if "'compliance_status': 'APPROVED'" in msg.content:
                    self.compliance_status = "APPROVED"
                    self.memory.update_workflow_state("compliance_passed", True)
                elif "'compliance_status': 'FAILED'" in msg.content:
                    self.compliance_status = "FAILED"

            if "Underwriting Result" in msg.content:
                if "'decision': 'APPROVED'" in msg.content:
                    self.underwriting_decision = "APPROVED"
                    self.memory.update_workflow_state("underwriting_decision", "APPROVED")
                elif "'decision': 'REJECTED'" in msg.content:
                    self.underwriting_decision = "REJECTED"
                    self.memory.update_workflow_state("underwriting_decision", "REJECTED")
                elif "'decision': 'PENDING_DOCUMENT'" in msg.content:
                    self.underwriting_decision = "PENDING_DOCUMENT"

            if "Pricing Result" in msg.content:
                if "'pricing_status': 'APPROVED'" in msg.content:
                    self.pricing_status = "APPROVED"
                    self.memory.update_workflow_state("pricing_approved", True)
                elif "'pricing_status': 'REJECTED'" in msg.content:
                    self.pricing_status = "REJECTED"

            if "Sanction Letter Result" in msg.content:
                if "'sanction_status': 'APPROVED'" in msg.content:
                    self.sanction_status = "APPROVED"
                    self.memory.update_workflow_state("sanction_generated", True)
                elif "'sanction_status': 'FAILED'" in msg.content:
                    self.sanction_status = "FAILED"

            if "eSign Result" in msg.content:
                if "'esign_status': 'SIGNED'" in msg.content:
                    self.esign_status = "SIGNED"
                    self.memory.update_workflow_state("documents_signed", True)

            if "Disbursement Result" in msg.content:
                if "'disbursement_status': 'SUCCESS'" in msg.content:
                    self.disbursement_status = "SUCCESS"
                    self.memory.update_workflow_state("disbursement_completed", True)

        # ------------------------------------
        # Hard gates - Rejection rules
        # ------------------------------------

        if "loan" in user_message.lower():

            if self.kyc_status == "FAILED":
                response = "I'm sorry, but your KYC verification failed. We cannot proceed with your loan application."
                self.memory.add_message("bot", response)
                return response

            if self.crm_status == "FAILED":
                response = "Your CRM details could not be verified. Please update your information and try again."
                self.memory.add_message("bot", response)
                return response

            if self.income_status == "FAILED":
                response = "Income verification failed. The EMI burden is too high for your salary. We cannot approve this amount."
                self.memory.add_message("bot", response)
                return response

            if self.compliance_status == "FAILED":
                response = "Your application did not pass compliance checks. We cannot proceed further."
                self.memory.add_message("bot", response)
                return response

            if self.underwriting_decision == "REJECTED":
                response = "Unfortunately, your loan application has been rejected during underwriting review."
                self.memory.add_message("bot", response)
                return response

            if self.underwriting_decision == "PENDING_DOCUMENT":
                response = "We need your salary slip to complete the underwriting process. Please upload it to proceed."
                self.memory.add_message("bot", response)
                self.memory.update_workflow_state("salary_slip_pending", True)
                return response

            if self.pricing_status == "REJECTED":
                response = "Your loan pricing calculation shows you're not eligible. Your EMI burden is too high relative to your income."
                self.memory.add_message("bot", response)
                return response

            if self.sanction_status == "FAILED":
                response = "We encountered an issue generating your sanction letter. Please try again later."
                self.memory.add_message("bot", response)
                return response

            if self.esign_status == "SIGNED":
                response = "Great! Your documents have been digitally signed. Proceeding with fund disbursement."
                self.memory.add_message("bot", response)
                return response

            if self.disbursement_status == "SUCCESS":
                response = "Excellent! Your loan has been approved and the funds will be transferred to your account within 1-2 business days."
                self.memory.add_message("bot", response)
                return response

        final_response = result["messages"][-1].content
        self.memory.add_message("bot", final_response)
        return final_response


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