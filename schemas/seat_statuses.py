from pydantic import BaseModel
from typing import Optional

class SeatStatusBase(BaseModel):
    name: str
    color: Optional[str] = None
    description: Optional[str] = None

class SeatStatusCreate(SeatStatusBase):
    pass

class SeatStatusUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None

class SeatStatusResponse(SeatStatusBase):
    id: int

    class Config:
        from_attributes = True