from fastapi import FastAPI, HTTPException
from typing import List
import json
from .models import Offer

app = FastAPI(title="Offer Mart API", version="1.0")

# Load dummy offers from JSON
with open("apis/offer_mart/data/offers.json", "r") as f:
    offers_db = json.load(f)

# ----------------------------------------------------
# GET /offers/{customer_id}
# Returns all offers for a specific customer
# ----------------------------------------------------
@app.get("/offers/{customer_id}", response_model=List[Offer])
def get_offers_for_customer(customer_id: str):
    customer_offers = [offer for offer in offers_db if offer["customer_id"] == customer_id]

    if not customer_offers:
        raise HTTPException(status_code=404, detail="No offers found for this customer")

    return customer_offers

# ----------------------------------------------------
# GET /offers
# Returns all offers (optional endpoint)
# ----------------------------------------------------
@app.get("/offers", response_model=List[Offer])
def list_all_offers():
    return offers_db

# ----------------------------------------------------
# POST /offers
# Add a new offer (optional for testing)
# ----------------------------------------------------
@app.post("/offers", response_model=Offer)
def create_offer(offer: Offer):
    offers_db.append(offer.dict())

    # Optionally save to file:
    with open("data/offers.json", "w") as f:
        json.dump(offers_db, f, indent=4)

    return offer
