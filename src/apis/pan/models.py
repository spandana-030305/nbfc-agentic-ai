from pydantic import BaseModel
from datetime import date

class PANRequest(BaseModel):
    pan: str
    name: str
    dob: date

class PANResponse(BaseModel):
    status: str
    message: str
