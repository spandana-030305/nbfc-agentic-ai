from fastapi import FastAPI, HTTPException
from typing import List
import json
from .models import Offer

app = FastAPI(
    title="Offer Mart API",
    version="1.0"
)

# -----------------------------------
# LOAD OFFERS FROM JSON
# -----------------------------------

with open("apis/offer_mart/data/offers.json", "r") as f:
    offers_db = json.load(f)

print("LOADED OFFERS:", offers_db)


# -----------------------------------
# GET /offers/{customer_id}
# -----------------------------------

@app.get(
    "/offers/{customer_id}",
    response_model=List[Offer]
)
def get_offers_for_customer(
    customer_id: str
):
    print(
        "REQUESTED CUSTOMER:",
        customer_id
    )

    customer_offers = [
        offer
        for offer in offers_db
        if offer["customer_id"] == customer_id
    ]

    print(
        "MATCHING OFFERS:",
        customer_offers
    )

    if not customer_offers:
        raise HTTPException(
            status_code=404,
            detail=(
                "No offers found "
                "for this customer"
            )
        )

    return customer_offers


# -----------------------------------
# GET /offers
# -----------------------------------

@app.get(
    "/offers",
    response_model=List[Offer]
)
def list_all_offers():
    return offers_db


# -----------------------------------
# POST /offers
# -----------------------------------

@app.post(
    "/offers",
    response_model=Offer
)
def create_offer(
    offer: Offer
):
    offers_db.append(
        offer.dict()
    )

    with open(
        "apis/offer_mart/data/offers.json",
        "w"
    ) as f:
        json.dump(
            offers_db,
            f,
            indent=4
        )

    return offer