from agents.income_agent import income_agent_task

def test_income_verification():
    customer_id = input("Enter customer ID: ")

    result = income_agent_task(customer_id)

    print("\nIncome Verification Result:")
    print(result)

if __name__ == "__main__":
    test_income_verification()
