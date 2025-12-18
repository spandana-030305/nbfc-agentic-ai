from fastapi import FastAPI
from .models import PANRequest, PANResponse
from pathlib import Path
import json
import re

app = FastAPI(title="Dummy PAN Verification API", version="1.0")

# Load PAN data once at startup
with open("apis/pan/data/pan.json", "r") as f:
    PAN_DB = json.load(f)

PAN_REGEX = r"^[A-Z]{5}[0-9]{4}[A-Z]$"

@app.post("/pan/verify", response_model=PANResponse)
def verify_pan(data: PANRequest):
    # Step 1: PAN format validation
    if not re.match(PAN_REGEX, data.pan):
        return PANResponse(
            status="FAILED",
            message="Invalid PAN format"
        )
    
    # Step 2: Search PAN in dummy DB
    record = next(
        (item for item in PAN_DB if item["pan"] == data.pan),
        None
    )

    if not record:
        return PANResponse(
            status="FAILED",
            message="PAN not found"
        )
    
    # Step 3: Name & DOB match
    if(
        record["name"].lower() != data.name.lower()
        or record["dob"] != str(data.dob)
    ):
        return PANResponse(
            status="FAILED",
            message="PAN details do not match"
        )
    
    # Step 4: Status check
    if record["status"] != "ACTIVE":
        return PANResponse(
            status="FAILED",
            message=f"PAN status is {record['status']}"
        )
    
    if record["status"] == "ACTIVE":    
        return PANResponse(
            status="VERIFIED",
            message="PAN verified successfully"
        )