from pydantic import BaseModel
from typing import Optional

class FloorBase(BaseModel):
    name: str

class FloorCreate(FloorBase):
    pass

class FloorUpdate(BaseModel):
    name: Optional[str] = None

class FloorResponse(FloorBase):
    id: int

    class Config:
        from_attributes = True