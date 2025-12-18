from agents.master_agent import MasterAgent

agent = MasterAgent()

# -------------------------
# Prompt 1: KYC
# -------------------------
kyc_prompt = """
Perform PAN-based KYC with the following details:
PAN: ABCDE1234F
NAME: Sai Spandana
DOB: 2003-05-14
"""

kyc_response = agent.run(kyc_prompt)

print("KYC Response:")
print(kyc_response)

customer_id = input("\nEnter customer ID: ")
# -------------------------
# Prompt 2: Sales (after KYC)
# -------------------------
sales_prompt = f"""
KYC is completed. Now fetch loan offers for customer {customer_id}.
"""

sales_response = agent.run(sales_prompt)

print("\nSales Response:")
print(sales_response)


