from pydantic import BaseModel

from app.schemas.auth import PhoneOutSchema


class UserResponseSchema(BaseModel):
    id: int
    tg_id: int
    tg_name: str
    contract_number: str
    full_name: str
    phones: list[PhoneOutSchema]
    
    
    class Config:
        from_attributes = True


class UserIDInputSchema(BaseModel):
    user_id: int