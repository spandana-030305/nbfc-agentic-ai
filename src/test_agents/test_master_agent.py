from agents.master_agent import MasterAgent

agent = MasterAgent()
response = agent.run("I want a personal loan for customer C001")  # Single string

print("Agent Response:", response)
