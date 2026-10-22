from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from app.core.config import settings


class SalaryRecordBase(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Salary amount, must be positive")
    currency: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency code")
    effective_from: date = Field(..., description="Inclusive effective start date")
    effective_to: Optional[date] = Field(None, description="Exclusive effective end date")
    change_reason: str = Field(..., min_length=2, max_length=100, description="Reason for change")
    is_correction: bool = Field(False, description="Flag indicating data correction vs standard change")
    correction_notes: Optional[str] = Field(None, max_length=500, description="Detailed correction reason")

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        upper = v.upper()
        if upper not in settings.SUPPORTED_CURRENCIES:
            raise ValueError(
                f"Unsupported currency: '{v}'. Must be one of {', '.join(settings.SUPPORTED_CURRENCIES)}"
            )
        return upper

    @model_validator(mode="after")
    def validate_dates(self) -> "SalaryRecordBase":
        if self.effective_to is not None and self.effective_to <= self.effective_from:
            raise ValueError("effective_to must be strictly greater than effective_from")
        return self


class SalaryCreate(SalaryRecordBase):
    pass


class SalaryResponse(SalaryRecordBase):
    id: int
    employee_id: int
    created_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
