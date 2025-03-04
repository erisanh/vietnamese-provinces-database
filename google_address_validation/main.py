import os

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from models import AddressInput, AddressValidationResponse

# Load environment variables from .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize FastAPI app
app = FastAPI(title="Address Validation API")

# URL of Google Address Validation API
VALIDATION_API_URL = "https://addressvalidation.googleapis.com/v1:validateAddress"

@app.post("/validate-address/", response_model=AddressValidationResponse)
async def validate_address(address: AddressInput):
    """
    Endpoint to validate an address using Google Address Validation API.
    Receives input address and returns the validated address.
    """
    # Create payload for Google API as per required format
    payload = {
        "address": {
            "regionCode": address.country.upper(),  # Country code (ISO 3166-1 alpha-2)
            "locality": address.city,
            "addressLines": [address.street],
            "administrativeArea": address.state,
            "postalCode": address.postal_code
        },
        "enableUspsCass": True  # Optional: use USPS standard if it's a US address
    }

    # Send request to Google API
    headers = {"Content-Type": "application/json"}
    params = {"key": GOOGLE_API_KEY}
    
    try:
        response = requests.post(
            VALIDATION_API_URL,
            json=payload,
            headers=headers,
            params=params
        )
        response.raise_for_status()  # Raise error if request was unsuccessful
        result = response.json()

        # Process result from Google API
        validation_result = result.get("result", {}).get("address", {})
        verdict = result.get("result", {}).get("verdict", {})

        # Normalized address
        formatted_address = validation_result.get("formattedAddress", "Unknown")
        is_valid = not verdict.get("inputGranularityTooCoarse", False)  # Basic validity check

        # Return response
        return AddressValidationResponse(
            formatted_address=formatted_address,
            is_valid=is_valid,
            message=verdict.get("validationGranularity", "Validated")
        )

    except requests.exceptions.HTTPError as e:
        # Handle errors from Google API
        error_detail = e.response.json().get("error", {}).get("message", "Unknown error")
        raise HTTPException(status_code=e.response.status_code, detail=error_detail)
    except Exception as e:
        # Handle other errors
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Run the application (used during debugging)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)