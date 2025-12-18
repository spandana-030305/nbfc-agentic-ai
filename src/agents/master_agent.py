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
    result = kyc_agent_task(pan=pan, name=name, dob=dob)
    return f"KYC Result: {result}"


@tool
def sales_agent_tool(customer_id: str) -> str:
    """
    Get best loan offers for customer ID (e.g., 'C001').
    """
    from agents.sales_agent import sales_agent_task
    offers = sales_agent_task(customer_id)
    return f"Found offers: {offers}"


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

        self.kyc_status = None

        tools = [
            kyc_agent_tool,     
            sales_agent_tool    
        ]

        checkpointer = MemorySaver()

        self.agent = create_agent(
            self.llm,
            tools,
            checkpointer=checkpointer
        )

    def run(self, user_message: str) -> str:
        config = {"configurable": {"thread_id": "1"}}
        result = self.agent.invoke(
            {"messages": [("user", user_message)]},
            config
        )

        # ----------------------------
        # Capture KYC result
        # ----------------------------
        for msg in result["messages"]:
            if isinstance(msg.content, str) and "KYC Result" in msg.content:
                if "'kyc_status': 'VERIFIED'" in msg.content:
                    self.kyc_status = "VERIFIED"
                elif "'kyc_status': 'FAILED'" in msg.content:
                    self.kyc_status = "FAILED"

        # ----------------------------
        # HARD COMPLIANCE GATE
        # ----------------------------
        if "loan" in user_message.lower():
            if self.kyc_status != "VERIFIED":
                return "Loan offers cannot be provided as KYC verification failed."

        return result["messages"][-1].content





