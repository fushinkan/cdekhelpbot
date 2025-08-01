from pydantic import BaseModel, ConfigDict

from app.schemas.auth import PhoneResponseSchema


class UserResponseSchema(BaseModel):
    id: int
    telegram_id: int | None = None
    telegram_name: str | None = None
    city: str
    contract_number: str
    contractor: str
    phones: list[PhoneResponseSchema]
    
    
    model_config = ConfigDict(from_attributes=True)

class PaginateUserResponse(BaseModel):
    total: int
    page: int
    per_page: int
    total_pages: int
    users: list[UserResponseSchema]


    model_config = ConfigDict(from_attributes=True)
        
class UserIDInputSchema(BaseModel):
    user_id: int