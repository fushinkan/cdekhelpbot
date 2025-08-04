from pydantic import BaseModel, ConfigDict


class AdminsResponseSchema(BaseModel):
    id: int
    tg_id: int | None = None
    tg_name: str | None = None
    full_name: str
    phone_number: str


    model_config = ConfigDict(from_attributes=True)