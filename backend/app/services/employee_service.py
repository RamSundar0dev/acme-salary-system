from datetime import date
from decimal import Decimal
from typing import Optional, Tuple, List
from fastapi import HTTPException, status
from sqlalchemy import func, or_, desc, asc
from sqlalchemy.orm import Session, joinedload

from app.models.employee import Employee
from app.models.department import Department
from app.models.salary_record import SalaryRecord
from app.models.user import User
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeSummary,
    EmployeeDetail,
    PaginatedEmployees,
)
from app.schemas.salary import SalaryCreate
from app.services.salary_service import SalaryService
from app.services.audit_service import AuditService

ALLOWED_SORT_COLUMNS = {
    "id": Employee.id,
    "employee_number": Employee.employee_number,
    "first_name": Employee.first_name,
    "last_name": Employee.last_name,
    "country_code": Employee.country_code,
    "employment_status": Employee.employment_status,
    "employment_start_date": Employee.employment_start_date,
}


class EmployeeService:
    @staticmethod
    def get_employees_paginated(
        db: Session,
        page: int = 1,
        page_size: int = 15,
        search: Optional[str] = None,
        country_code: Optional[str] = None,
        department_id: Optional[int] = None,
        employment_status: Optional[str] = None,
        sort_by: str = "employee_number",
        sort_order: str = "asc",
    ) -> PaginatedEmployees:
        # Enforce page size boundaries
        if page < 1:
            page = 1
        page_size = max(1, min(page_size, 100))
        offset = (page - 1) * page_size

        # Query base: join employee with department and current active salary
        query = (
            db.query(
                Employee.id,
                Employee.employee_number,
                Employee.first_name,
                Employee.last_name,
                Employee.email,
                Employee.country_code,
                Employee.department_id,
                Department.name.label("department_name"),
                Employee.employment_status,
                Employee.employment_start_date,
                SalaryRecord.amount.label("current_salary"),
                SalaryRecord.currency.label("currency"),
                SalaryRecord.effective_from.label("effective_from"),
            )
            .join(Department, Employee.department_id == Department.id)
            .outerjoin(
                SalaryRecord,
                (SalaryRecord.employee_id == Employee.id)
                & (SalaryRecord.effective_to.is_(None)),
            )
        )

        # Apply Filters
        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Employee.employee_number.ilike(search_pattern),
                    Employee.first_name.ilike(search_pattern),
                    Employee.last_name.ilike(search_pattern),
                    Employee.email.ilike(search_pattern),
                )
            )
        if country_code:
            query = query.filter(Employee.country_code == country_code.upper())
        if department_id:
            query = query.filter(Employee.department_id == department_id)
        if employment_status:
            query = query.filter(Employee.employment_status == employment_status.upper())

        # Total count before pagination
        total = query.count()

        # Sorting
        sort_col = ALLOWED_SORT_COLUMNS.get(sort_by, Employee.employee_number)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_col))
        else:
            query = query.order_by(asc(sort_col))

        rows = query.offset(offset).limit(page_size).all()

        items = [
            EmployeeSummary(
                id=r.id,
                employee_number=r.employee_number,
                first_name=r.first_name,
                last_name=r.last_name,
                full_name=f"{r.first_name} {r.last_name}",
                email=r.email,
                country_code=r.country_code,
                department_id=r.department_id,
                department_name=r.department_name,
                employment_status=r.employment_status,
                employment_start_date=r.employment_start_date,
                current_salary=r.current_salary,
                currency=r.currency,
                effective_from=r.effective_from,
            )
            for r in rows
        ]

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return PaginatedEmployees(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @staticmethod
    def get_employee_detail(db: Session, employee_id: int) -> EmployeeDetail:
        emp = (
            db.query(Employee)
            .options(joinedload(Employee.department), joinedload(Employee.salary_records))
            .filter(Employee.id == employee_id)
            .first()
        )
        if not emp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee {employee_id} not found",
            )

        # Find current active salary
        current_sal = next((s for s in emp.salary_records if s.effective_to is None), None)

        return EmployeeDetail(
            id=emp.id,
            employee_number=emp.employee_number,
            first_name=emp.first_name,
            last_name=emp.last_name,
            full_name=f"{emp.first_name} {emp.last_name}",
            email=emp.email,
            country_code=emp.country_code,
            department=emp.department,
            employment_status=emp.employment_status,
            employment_start_date=emp.employment_start_date,
            current_salary=current_sal.amount if current_sal else None,
            currency=current_sal.currency if current_sal else None,
            created_at=emp.created_at,
            updated_at=emp.updated_at,
            salary_history=emp.salary_records,
        )

    @staticmethod
    def create_employee(
        db: Session,
        employee_in: EmployeeCreate,
        current_user: User,
        ip_address: Optional[str] = None,
    ) -> Employee:
        # Check duplicate employee_number or email
        existing = (
            db.query(Employee)
            .filter(
                or_(
                    Employee.employee_number == employee_in.employee_number,
                    Employee.email == employee_in.email.lower(),
                )
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee number or email already registered.",
            )

        emp = Employee(
            employee_number=employee_in.employee_number,
            first_name=employee_in.first_name,
            last_name=employee_in.last_name,
            email=employee_in.email.lower(),
            country_code=employee_in.country_code.upper(),
            department_id=employee_in.department_id,
            employment_status=employee_in.employment_status.upper(),
            employment_start_date=employee_in.employment_start_date,
        )
        db.add(emp)
        db.flush()

        AuditService.log_action(
            db=db,
            actor=current_user,
            action="EMPLOYEE_CREATE",
            entity_type="employee",
            entity_id=emp.id,
            change_data={
                "employee_number": emp.employee_number,
                "name": f"{emp.first_name} {emp.last_name}",
                "department_id": emp.department_id,
                "country_code": emp.country_code,
            },
            ip_address=ip_address,
        )

        # If initial salary provided, create initial salary record
        if employee_in.initial_salary and employee_in.initial_currency:
            SalaryService.record_salary_change(
                db=db,
                employee_id=emp.id,
                salary_data=SalaryCreate(
                    amount=employee_in.initial_salary,
                    currency=employee_in.initial_currency,
                    effective_from=emp.employment_start_date,
                    effective_to=None,
                    change_reason="INITIAL_OFFER",
                    is_correction=False,
                ),
                current_user=current_user,
                ip_address=ip_address,
            )

        db.commit()
        db.refresh(emp)
        return emp

    @staticmethod
    def update_employee(
        db: Session,
        employee_id: int,
        employee_in: EmployeeUpdate,
        current_user: User,
        ip_address: Optional[str] = None,
    ) -> Employee:
        emp = db.query(Employee).filter(Employee.id == employee_id).first()
        if not emp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee {employee_id} not found",
            )

        changes = {}
        for field, val in employee_in.dict(exclude_unset=True).items():
            if val is not None:
                old_val = getattr(emp, field)
                if old_val != val:
                    changes[field] = {"old": str(old_val), "new": str(val)}
                    setattr(emp, field, val)

        if changes:
            AuditService.log_action(
                db=db,
                actor=current_user,
                action="EMPLOYEE_UPDATE",
                entity_type="employee",
                entity_id=emp.id,
                change_data=changes,
                ip_address=ip_address,
            )
            db.commit()
            db.refresh(emp)

        return emp
