from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_hr_manager, get_db
from app.models.department import Department
from app.models.user import User
from app.schemas.department import DepartmentResponse
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeDetail,
    EmployeeUpdate,
    PaginatedEmployees,
)
from app.schemas.salary import SalaryCreate, SalaryResponse
from app.services.employee_service import EmployeeService
from app.services.salary_service import SalaryService

router = APIRouter(tags=["Employees & Compensation"])


@router.get("/departments", response_model=List[DepartmentResponse])
def get_all_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_manager),
):
    return db.query(Department).order_by(Department.name.asc()).all()


@router.get("/employees", response_model=PaginatedEmployees)
def list_employees(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(15, ge=1, le=100, description="Records per page"),
    search: Optional[str] = Query(None, description="Search by name, number, email"),
    country_code: Optional[str] = Query(None, description="Filter by 2-letter country code"),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    employment_status: Optional[str] = Query(None, description="Filter by status (ACTIVE, TERMINATED, etc)"),
    sort_by: str = Query("employee_number", description="Column to sort by"),
    sort_order: str = Query("asc", description="asc or desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_manager),
):
    return EmployeeService.get_employees_paginated(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        country_code=country_code,
        department_id=department_id,
        employment_status=employment_status,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.post("/employees", status_code=status.HTTP_201_CREATED)
def create_new_employee(
    employee_in: EmployeeCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_manager),
):
    ip_addr = request.client.host if request.client else None
    return EmployeeService.create_employee(
        db=db,
        employee_in=employee_in,
        current_user=current_user,
        ip_address=ip_addr,
    )


@router.get("/employees/{employee_id}", response_model=EmployeeDetail)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_manager),
):
    return EmployeeService.get_employee_detail(db=db, employee_id=employee_id)


@router.patch("/employees/{employee_id}")
def update_employee(
    employee_id: int,
    employee_in: EmployeeUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_manager),
):
    ip_addr = request.client.host if request.client else None
    return EmployeeService.update_employee(
        db=db,
        employee_id=employee_id,
        employee_in=employee_in,
        current_user=current_user,
        ip_address=ip_addr,
    )


@router.get("/employees/{employee_id}/salaries", response_model=List[SalaryResponse])
def get_employee_salary_history(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_manager),
):
    return SalaryService.get_salary_history(db=db, employee_id=employee_id)


@router.post("/employees/{employee_id}/salaries", response_model=SalaryResponse, status_code=status.HTTP_201_CREATED)
def record_employee_salary(
    employee_id: int,
    salary_in: SalaryCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_manager),
):
    ip_addr = request.client.host if request.client else None
    return SalaryService.record_salary_change(
        db=db,
        employee_id=employee_id,
        salary_data=salary_in,
        current_user=current_user,
        ip_address=ip_addr,
    )
