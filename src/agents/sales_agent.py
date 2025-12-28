from autogen_agentchat.agents import UserProxyAgent
import requests

OFFER_MART_URL = "http://localhost:8001/offers"


class SalesAgent(UserProxyAgent):
    def __init__(self):
        super().__init__(name="SalesAgent")

    def fetch_offers(self, customer_id: str):
        url = f"{OFFER_MART_URL}/{customer_id}"
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            offers = resp.json()
        except requests.RequestException:
            # Any HTTP / network / timeout error
            return {"offers": []}

        if not offers:
            return {"offers": []}

        best_offer = min(offers, key=lambda o: o["apr"])
        return {"offers": [best_offer]}


sales_agent = SalesAgent()


def sales_agent_task(customer_id: str):
    return sales_agent.fetch_offers(customer_id)

