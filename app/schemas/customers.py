from pydantic import BaseModel, ConfigDict

from app.schemas.auth import PhoneInputSchema, PhoneResponseSchema


class CustomerInputSchema(BaseModel):
    contractor: str
    city: str
    contract_number: str
    number: list[PhoneInputSchema]
    

class CustomerResponseSchema(BaseModel):
    id: int
    contractor: str
    city: str
    contract_number: str
    number: list[PhoneResponseSchema]
    
    model_config = ConfigDict(from_attributes=True)
    
