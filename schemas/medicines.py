from pydantic import BaseModel, Field
from typing import Optional

class MedicineCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    strength: str = Field(..., min_length=1, max_length=50)
    form: str = Field(..., min_length=1, max_length=50)
    generic_name: Optional[str] = Field(None, max_length=200)


class MedicineResponse(BaseModel):
    id: int
    name: str
    strength: str
    form: str
    generic_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True