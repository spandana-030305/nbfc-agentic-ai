# main.py

from agents.sales_agent import sales_agent_task

if __name__ == "__main__":
    customer_id = input("Enter customer ID: ")
    result = sales_agent_task(customer_id)
    print("Best offer:", result)




