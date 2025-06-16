from pydantic import BaseModel, Field, field_validator
from typing import Optional

class CreateRowsRequest(BaseModel):
    section_id: int
    quantity: int = Field(..., gt=0, description="Количество создаваемых рядов")
    start_number: Optional[int] = Field(
        None, gt=0, description="Номер первого ряда (если не задан — продолжит после последнего)"
    )

class CreateSeatsByRowNumberRequest(BaseModel):
    section_id: int
    start_row_number: int = Field(..., gt=0)
    end_row_number: int = Field(..., gt=0)
    start_number: int = Field(..., gt=0)
    end_number: int = Field(..., gt=0)

    @field_validator("end_row_number")
    @classmethod
    def check_row_range(cls, v, info):
        start = info.data.get("start_row_number")
        if start is not None and v < start:
            raise ValueError("end_row_number должен быть >= start_row_number")
        return v

    @field_validator("end_number")
    @classmethod
    def check_seat_range(cls, v, info):
        start = info.data.get("start_number")
        if start is not None and v < start:
            raise ValueError("end_number должен быть >= start_number")
        return v