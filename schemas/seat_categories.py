from pydantic import BaseModel
from typing import Optional

class SeatCategoryBase(BaseModel):
    name: str
    color: str
    price: float

class SeatCategoryCreate(SeatCategoryBase):
    pass

class SeatCategoryUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    price: Optional[float] = None

class SeatCategoryResponse(SeatCategoryBase):
    id: int

    class Config:
        from_attributes = True