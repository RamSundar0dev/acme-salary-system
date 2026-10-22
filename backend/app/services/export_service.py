import csv
import io
from typing import Generator, Optional
from sqlalchemy.orm import Session
from app.models.employee import Employee
from app.models.department import Department
from app.models.salary_record import SalaryRecord


class ExportService:
    @staticmethod
    def stream_employees_csv(
        db: Session,
        country_code: Optional[str] = None,
        department_id: Optional[int] = None,
        employment_status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Generator[str, None, None]:
        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        writer.writerow([
            "Employee Number",
            "First Name",
            "Last Name",
            "Email",
            "Country",
            "Department",
            "Status",
            "Start Date",
            "Current Salary",
            "Currency",
            "Effective Date",
        ])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        query = (
            db.query(
                Employee.employee_number,
                Employee.first_name,
                Employee.last_name,
                Employee.email,
                Employee.country_code,
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

        if country_code:
            query = query.filter(Employee.country_code == country_code.upper())
        if department_id:
            query = query.filter(Employee.department_id == department_id)
        if employment_status:
            query = query.filter(Employee.employment_status == employment_status.upper())
        if search:
            search_pat = f"%{search.strip()}%"
            query = query.filter(
                (Employee.employee_number.ilike(search_pat))
                | (Employee.first_name.ilike(search_pat))
                | (Employee.last_name.ilike(search_pat))
                | (Employee.email.ilike(search_pat))
            )

        query = query.order_by(Employee.employee_number.asc())

        # Yield in batches of 500 rows to keep memory constant
        batch_size = 500
        offset = 0

        while True:
            rows = query.offset(offset).limit(batch_size).all()
            if not rows:
                break
            for r in rows:
                writer.writerow([
                    r.employee_number,
                    r.first_name,
                    r.last_name,
                    r.email,
                    r.country_code,
                    r.department_name,
                    r.employment_status,
                    str(r.employment_start_date),
                    str(r.current_salary) if r.current_salary is not None else "",
                    r.currency or "",
                    str(r.effective_from) if r.effective_from is not None else "",
                ])
                yield output.getvalue()
                output.seek(0)
                output.truncate(0)
            offset += batch_size
