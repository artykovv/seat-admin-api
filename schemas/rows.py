from pydantic import BaseModel
from typing import Optional

class RowBase(BaseModel):
    section_id: int
    number: int

class RowCreate(RowBase):
    pass

class RowUpdate(BaseModel):
    section_id: Optional[int] = None
    number: Optional[int] = None

class RowResponse(RowBase):
    id: int

    class Config:
        from_attributes = True