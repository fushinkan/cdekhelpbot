from pydantic import BaseModel

class UsersSchema(BaseModel):
    """
    Схема для представления пользователя из БД.
    """
    id: int
    contractor: str
    phone_number: str
    contract_number: str
    
    class Config:
        from_attributes = True