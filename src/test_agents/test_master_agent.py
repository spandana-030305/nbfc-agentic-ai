from agents.master_agent import MasterAgent

agent = MasterAgent()

# Take KYC details from user
pan = input("Enter PAN: ").strip()
name = input("Enter Name: ").strip()
dob = input("Enter DOB (YYYY-MM-DD): ").strip()

kyc_prompt = f"""
Perform PAN-based KYC with the following details:
PAN: {pan}
NAME: {name}
DOB: {dob}
"""

kyc_response = agent.run(kyc_prompt)
print("KYC Response:")
print(kyc_response)

customer_id = input("\nEnter customer ID: ").strip()

income_prompt = f"""
Verify income eligibility for customer {customer_id}
by fetching bank statements.
"""
income_response = agent.run(income_prompt)
print("\nIncome Verification Response:")
print(income_response)

sales_prompt = f"""
KYC is completed. Now fetch loan offers for customer {customer_id}.
"""
sales_response = agent.run(sales_prompt)
print("\nSales Response:")
print(sales_response)




