import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import create_access_token, get_password_hash


@pytest.fixture(scope="session")
def db_session():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def admin_user(db_session: Session) -> User:
    user = db_session.query(User).filter(User.email == "hr.manager@acme.corp").first()
    if not user:
        user = User(
            email="hr.manager@acme.corp",
            password_hash=get_password_hash("AcmeHR2026!SecurePass"),
            full_name="HR Operations Manager",
            role="hr_manager",
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


@pytest.fixture(scope="session")
def auth_headers(admin_user: User):
    token = create_access_token(subject=str(admin_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def temp_employee(db_session: Session):
    from datetime import date
    from app.models.employee import Employee
    from app.models.salary_record import SalaryRecord
    from app.models.department import Department

    dept = db_session.query(Department).first()
    emp = Employee(
        employee_number=f"ACM-TMP-{int(date.today().strftime('%Y%m%d'))}-{id(db_session) % 10000}",
        first_name="Test",
        last_name="Worker",
        email=f"test.worker.{id(db_session) % 10000}@acme.corp",
        country_code="US",
        department_id=dept.id,
        employment_status="ACTIVE",
        employment_start_date=date(2023, 1, 1),
    )
    db_session.add(emp)
    db_session.flush()

    initial_sal = SalaryRecord(
        employee_id=emp.id,
        amount=Decimal("100000.00"),
        currency="USD",
        effective_from=date(2023, 1, 1),
        effective_to=None,
        change_reason="INITIAL_OFFER",
        is_correction=False,
    )
    db_session.add(initial_sal)
    db_session.commit()
    db_session.refresh(emp)

    yield emp

    # Cleanup
    db_session.query(SalaryRecord).filter(SalaryRecord.employee_id == emp.id).delete()
    db_session.query(Employee).filter(Employee.id == emp.id).delete()
    db_session.commit()

