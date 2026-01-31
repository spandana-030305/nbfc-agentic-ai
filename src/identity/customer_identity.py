import json
import os
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUSTOMERS_FILE = os.path.join(BASE_DIR, "data", "customers.json")


def load_customers():
    if not os.path.exists(CUSTOMERS_FILE):
        return []
    with open(CUSTOMERS_FILE, "r") as f:
        return json.load(f)


def save_customers(customers):
    with open(CUSTOMERS_FILE, "w") as f:
        json.dump(customers, f, indent=2)


def resolve_customer_id(email: str) -> str:
    """
    Internal identity resolver
    Input  : email (from federated login)
    Output : customer_id (internal)
    """

    customers = load_customers()

    for customer in customers:
        if customer["email"] == email:
            return customer["customer_id"]

    # New customer (first-time login)
    new_customer_id = f"C{str(uuid.uuid4())[:6].upper()}"

    customers.append({
        "customer_id": new_customer_id,
        "email": email,
        "login_provider": "google"
    })

    save_customers(customers)
    return new_customer_id
