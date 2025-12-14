from autogen_agentchat.agents import UserProxyAgent
import requests

OFFER_MART_URL = "http://localhost:8001/offers"

class SalesAgent(UserProxyAgent):
    def __init__(self):
        super().__init__(name="SalesAgent")

    def fetch_offers(self, customer_id: str):
        url = f"{OFFER_MART_URL}/{customer_id}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        offers = response.json()
        if not offers:
            return {"offers": []}
        best_offer = min(offers, key=lambda o: o["apr"])
        return {"offers": [best_offer]}

sales_agent = SalesAgent()
# set these if supported in your version
# sales_agent.human_input_mode = "NEVER"
# sales_agent.code_execution_enabled = False

def sales_agent_task(customer_id: str):
    return sales_agent.fetch_offers(customer_id)


