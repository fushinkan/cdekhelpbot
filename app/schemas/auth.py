from pydantic import BaseModel, Field, ConfigDict


class LoginRequestSchema(BaseModel):
    phone_number: str = Field(..., example="79042803001")
    plain_password: str = Field(..., min_length=8)
    telegram_id: int | None = None
    telegram_name: str | None = None


class LoginStatusSchema(BaseModel):
    is_logged: bool
    telegram_id: int | None = None
    telegram_name: str | None = None


class PhoneInputSchema(BaseModel):
    phone_number: str

   
class PasswordInputSchema(BaseModel):
    user_id: int
    plain_password: str = Field(min_length=8)
 
 
class AcceptPasswordSchema(BaseModel):
    user_id: int
    phone_number: str
    password: str
    telegram_id: int | None = None
    telegram_name: str | None = None


class ConfirmPasswordSchema(BaseModel):
    user_id: int
    plain_password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)


class TelegramIDInputSchema(BaseModel):
    tg_id: int
    

class PhoneResponseSchema(BaseModel):
    id: int
    number: str
    
    model_config = ConfigDict(from_attributes=True)