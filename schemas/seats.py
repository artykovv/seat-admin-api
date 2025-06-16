from pydantic import BaseModel
from typing import Optional

class SeatBase(BaseModel):
    number: int
    category_id: int
    status_id: Optional[int] = None
    row_id: Optional[int] = None

class SeatCreate(SeatBase):
    pass

class SeatUpdate(BaseModel):
    number: Optional[int] = None
    category_id: Optional[int] = None
    status_id: Optional[int] = None

class SeatResponse(BaseModel):
    id: int
    number: int
    category_id: int
    status_id: int

    class Config:
        from_attributes = True