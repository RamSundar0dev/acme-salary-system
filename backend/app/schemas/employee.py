from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from app.schemas.department import DepartmentResponse
from app.schemas.salary import SalaryResponse


class EmployeeBase(BaseModel):
    employee_number: str = Field(..., min_length=3, max_length=30)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    country_code: str = Field(..., min_length=2, max_length=2)
    department_id: int
    employment_status: str = Field(default="ACTIVE")
    employment_start_date: date


class EmployeeCreate(EmployeeBase):
    initial_salary: Optional[Decimal] = Field(None, gt=0)
    initial_currency: Optional[str] = Field(None, min_length=3, max_length=3)


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    country_code: Optional[str] = Field(None, min_length=2, max_length=2)
    department_id: Optional[int] = None
    employment_status: Optional[str] = None


class EmployeeSummary(BaseModel):
    id: int
    employee_number: str
    first_name: str
    last_name: str
    full_name: str
    email: str
    country_code: str
    department_id: int
    department_name: str
    employment_status: str
    employment_start_date: date
    current_salary: Optional[Decimal] = None
    currency: Optional[str] = None
    effective_from: Optional[date] = None

    class Config:
        from_attributes = True


class EmployeeDetail(BaseModel):
    id: int
    employee_number: str
    first_name: str
    last_name: str
    full_name: str
    email: str
    country_code: str
    department: DepartmentResponse
    employment_status: str
    employment_start_date: date
    current_salary: Optional[Decimal] = None
    currency: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    salary_history: List[SalaryResponse] = []

    class Config:
        from_attributes = True


class PaginatedEmployees(BaseModel):
    items: List[EmployeeSummary]
    total: int
    page: int
    page_size: int
    total_pages: int
