from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

@tool
def sales_agent_tool(customer_id: str) -> str:
    """Get best loan offers for customer ID (e.g., 'C001')."""
    from agents.sales_agent import sales_agent_task
    offers = sales_agent_task(customer_id)
    return f"Found offers: {offers}"

class MasterAgent:
    def __init__(self):
        self.llm = ChatOllama(
            model="llama3.1:8b",
            temperature=0.1,
            base_url="http://localhost:11434",
        )
        
        tools = [sales_agent_tool]
        
        checkpointer = MemorySaver()
        self.agent = create_react_agent(
            self.llm,
            tools,
            checkpointer=checkpointer
        )


    def run(self, user_message: str) -> str:
        """Entry point for API Gateway"""
        config = {"configurable": {"thread_id": "1"}}
        result = self.agent.invoke({"messages": [("user", user_message)]}, config)
        return result["messages"][-1].content