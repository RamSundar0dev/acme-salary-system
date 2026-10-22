from sqlalchemy.orm import Session
from app.models.employee import Employee
from app.models.department import Department
from app.models.salary_record import SalaryRecord


def test_seed_employee_count_is_exactly_ten_thousand(db_session: Session):
    count = db_session.query(Employee).count()
    assert count == 10000, f"Expected exactly 10,000 seeded employees, found {count}"


def test_seed_departments_exist(db_session: Session):
    count = db_session.query(Department).count()
    assert count == 8, f"Expected 8 enterprise departments, found {count}"


def test_seed_unique_employee_numbers(db_session: Session):
    total = db_session.query(Employee.employee_number).count()
    distinct = db_session.query(Employee.employee_number).distinct().count()
    assert total == distinct == 10000, "All employee numbers must be unique"


def test_seed_active_salaries_present(db_session: Session):
    # Every employee must have an active current salary record (effective_to IS NULL)
    active_salaries = (
        db_session.query(SalaryRecord)
        .filter(SalaryRecord.effective_to.is_(None))
        .count()
    )
    assert active_salaries == 10000, f"Expected 10,000 active salary records, found {active_salaries}"
