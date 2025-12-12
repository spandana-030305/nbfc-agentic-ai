from pydantic import BaseModel

class Offer(BaseModel):
    offer_id: str
    customer_id: str
    amount: int
    tenure_months: int
    apr: float
    preapproved: bool = True
