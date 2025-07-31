from pydantic import BaseModel


class SaveInvoiceSchema(BaseModel):
    departure_city: str
    recipient_city: str
    invoice_number: str
    telegram_file_id: str