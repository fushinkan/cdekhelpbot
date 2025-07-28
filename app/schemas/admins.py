from pydantic import BaseModel

class AdminsResonseSchema(BaseModel):
    id: int
    tg_id: int | None = None
    tg_name: str | None = None
    full_name: str
    phone_number: str
    
    class Config:
        from_attributes = True
