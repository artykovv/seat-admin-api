from pydantic import BaseModel
from typing import Optional

class SectionBase(BaseModel):
    floor_id: int
    name: str

class SectionCreate(SectionBase):
    pass

class SectionUpdate(BaseModel):
    floor_id: Optional[int] = None
    name: Optional[str] = None

class SectionResponse(SectionBase):
    id: int

    class Config:
        from_attributes = True