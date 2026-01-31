import os
import json
from identity.customer_identity import resolve_customer_id, load_customers

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUSTOMERS_FILE = os.path.join(BASE_DIR, "data", "customers.json")


def reset_customers():
    with open(CUSTOMERS_FILE, "w") as f:
        json.dump([], f)


def test_new_customer():
    reset_customers()

    email = "testuser@gmail.com"
    customer_id = resolve_customer_id(email)

    assert customer_id is not None
    assert customer_id.startswith("C")

    customers = load_customers()
    assert len(customers) == 1
    assert customers[0]["email"] == email


def test_existing_customer():
    reset_customers()

    email = "repeat@gmail.com"
    first_id = resolve_customer_id(email)
    second_id = resolve_customer_id(email)

    assert first_id == second_id
