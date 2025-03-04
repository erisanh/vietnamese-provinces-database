from typing import Optional

from pydantic import BaseModel


class AddressInput(BaseModel):
    street: str
    city: str
    state: Optional[str] = None 
    postal_code: Optional[str] = None
    country: str

class AddressValidationResponse(BaseModel):
    formatted_address: str
    is_valid: bool
    message: Optional[str] = None