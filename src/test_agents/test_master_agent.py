from agents.master_agent import MasterAgent

# Initialize Master Agent
agent = MasterAgent()

# -------------------------------------------------
# STEP 1: KYC VERIFICATION
# -------------------------------------------------

print("\n========== KYC VERIFICATION ==========\n")

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

print("\nKYC RESPONSE:")
print(kyc_response)


# -------------------------------------------------
# STEP 2: INCOME VERIFICATION
# -------------------------------------------------

print("\n========== INCOME VERIFICATION ==========\n")

customer_id = input("Enter Customer ID: ").strip()

income_prompt = f"""
Verify income eligibility for customer {customer_id}
by fetching bank statements.
"""

income_response = agent.run(income_prompt)

print("\nINCOME VERIFICATION RESPONSE:")
print(income_response)


# -------------------------------------------------
# STEP 3: COMPLIANCE VERIFICATION
# -------------------------------------------------

print("\n========== COMPLIANCE VERIFICATION ==========\n")

compliance_prompt = f"""
Perform compliance verification for customer {customer_id}.

Check:
- KYC status
- Blacklist status
- Credit score eligibility
"""

compliance_response = agent.run(compliance_prompt)

print("\nCOMPLIANCE RESPONSE:")
print(compliance_response)


# -------------------------------------------------
# STEP 4: UNDERWRITING EVALUATION
# -------------------------------------------------

print("\n========== UNDERWRITING EVALUATION ==========\n")

credit_score = int(input("Enter Credit Score: ").strip())

income_status = input(
    "Enter Income Status (VERIFIED / FAILED): "
).strip().upper()

emi_ratio = float(
    input("Enter EMI Ratio (example: 0.35): ").strip()
)

underwriting_prompt = f"""
Perform underwriting evaluation for customer {customer_id}.

Credit Score: {credit_score}
Income Status: {income_status}
EMI Ratio: {emi_ratio}
"""

underwriting_response = agent.run(underwriting_prompt)

print("\nUNDERWRITING RESPONSE:")
print(underwriting_response)


# -------------------------------------------------
# STEP 5: PRICING EVALUATION
# -------------------------------------------------

print("\n========== PRICING EVALUATION ==========\n")

pricing_prompt = f"""
Calculate loan pricing for customer {customer_id}.

Generate:
- Eligible loan amount
- Interest rate
- Recommended tenure
- EMI eligibility
"""

pricing_response = agent.run(pricing_prompt)

print("\nPRICING RESPONSE:")
print(pricing_response)


# -------------------------------------------------
# STEP 6: SALES / LOAN OFFERS
# -------------------------------------------------

print("\n========== LOAN OFFERS ==========\n")

sales_prompt = f"""
KYC, Compliance, Underwriting, and Pricing
are completed.

Now fetch best loan offers for customer {customer_id}.
"""

sales_response = agent.run(sales_prompt)

print("\nSALES RESPONSE:")
print(sales_response)


# -------------------------------------------------
# STEP 7: SANCTION LETTER GENERATION
# -------------------------------------------------

print("\n========== SANCTION LETTER ==========\n")

customer_name = input(
    "Enter Customer Name for Sanction Letter: "
).strip()

loan_amount = float(
    input("Enter Approved Loan Amount: ").strip()
)

interest_rate = float(
    input("Enter Interest Rate: ").strip()
)

tenure_months = int(
    input("Enter Tenure (Months): ").strip()
)

underwriting_decision = input(
    "Enter Underwriting Decision "
    "(APPROVED / REJECTED / REVIEW): "
).strip().upper()

pricing_status = input(
    "Enter Pricing Status "
    "(APPROVED / FAILED / REJECTED): "
).strip().upper()

sanction_prompt = f"""
Generate sanction letter for customer.

Customer ID: {customer_id}
Customer Name: {customer_name}

Loan Amount: {loan_amount}
Interest Rate: {interest_rate}
Tenure Months: {tenure_months}

Underwriting Decision: {underwriting_decision}
Pricing Status: {pricing_status}
"""

sanction_response = agent.run(sanction_prompt)

print("\nSANCTION LETTER RESPONSE:")
print(sanction_response)


# -------------------------------------------------
# FINAL STATUS
# -------------------------------------------------

print("\n========== FINAL LOAN STATUS ==========\n")

print("KYC STATUS:", agent.kyc_status)

print("INCOME STATUS:", agent.income_status)

print("COMPLIANCE STATUS:", agent.compliance_status)

print("UNDERWRITING DECISION:",
      agent.underwriting_decision)

print("PRICING STATUS:",
      agent.pricing_status)

print("SANCTION STATUS:",
      agent.sanction_status)

print("\n========== PROCESS COMPLETED ==========\n")