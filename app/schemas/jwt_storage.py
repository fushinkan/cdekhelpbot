from pydantic import BaseModel


class TokenSaveSchema(BaseModel):
    access_token: str
    refresh_token: str
    user_id: int
    
    
class TokenSaveResponse(BaseModel):
    message: str
    user_id: int
    
class RefreshAccessTokenSchema(BaseModel):
    user_id: int
    refresh_token: str
    
class TokenClearSchema(BaseModel):
    user_id: int