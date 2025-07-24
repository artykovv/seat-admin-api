from typing import Optional
from pydantic import BaseModel

class TicketResponse(BaseModel):
    id: int
    client_full_name: str
    client_phone_number: str
    project_name: str
    project_id: int
    project_date_id: int
    project_date: str
    payment_status: Optional[str]
    amount: Optional[int]
    seats: list[dict]