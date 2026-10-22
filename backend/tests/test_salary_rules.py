from datetime import date, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.salary_record import SalaryRecord
from app.models.audit_log import AuditLog


def test_salary_must_be_positive(client: TestClient, auth_headers: dict, db_session: Session):
    emp = db_session.query(Employee).first()
    # Attempting to post negative or zero salary
    response = client.post(
        f"/api/v1/employees/{emp.id}/salaries",
        headers=auth_headers,
        json={
            "amount": -5000,
            "currency": "USD",
            "effective_from": "2026-11-01",
            "change_reason": "INVALID_TEST",
        },
    )
    assert response.status_code == 422


def test_salary_rejects_unsupported_currency(client: TestClient, auth_headers: dict, db_session: Session):
    emp = db_session.query(Employee).first()
    response = client.post(
        f"/api/v1/employees/{emp.id}/salaries",
        headers=auth_headers,
        json={
            "amount": 95000,
            "currency": "XYZ",  # Unsupported currency
            "effective_from": "2026-11-01",
            "change_reason": "INVALID_CURRENCY",
        },
    )
    assert response.status_code == 422


def test_salary_rejects_invalid_date_order(client: TestClient, auth_headers: dict, db_session: Session):
    emp = db_session.query(Employee).first()
    response = client.post(
        f"/api/v1/employees/{emp.id}/salaries",
        headers=auth_headers,
        json={
            "amount": 95000,
            "currency": "USD",
            "effective_from": "2026-11-01",
            "effective_to": "2026-10-01",  # effective_to before effective_from
            "change_reason": "INVALID_DATES",
        },
    )
    assert response.status_code == 422


def test_record_salary_increase_preserves_history_and_updates_previous(
    client: TestClient, auth_headers: dict, db_session: Session, temp_employee
):
    emp = temp_employee
    initial_salaries_count = len(emp.salary_records)
    current_sal = next(s for s in emp.salary_records if s.effective_to is None)
    old_amount = current_sal.amount

    new_effective_date = current_sal.effective_from + timedelta(days=180)
    new_amount = old_amount + Decimal("15000.00")

    response = client.post(
        f"/api/v1/employees/{emp.id}/salaries",
        headers=auth_headers,
        json={
            "amount": float(new_amount),
            "currency": current_sal.currency,
            "effective_from": str(new_effective_date),
            "change_reason": "PROMOTION",
            "is_correction": False,
        },
    )
    assert response.status_code == 201
    created_data = response.json()
    assert Decimal(str(created_data["amount"])) == new_amount

    # Verify database state
    db_session.expire_all()
    updated_records = (
        db_session.query(SalaryRecord)
        .filter(SalaryRecord.employee_id == emp.id)
        .order_by(SalaryRecord.effective_from.asc())
        .all()
    )
    assert len(updated_records) == initial_salaries_count + 1

    # Verify old active record now has effective_to set to new_effective_date
    prior_rec = [r for r in updated_records if r.id == current_sal.id][0]
    assert prior_rec.effective_to == new_effective_date

    # Verify audit log was created
    audit = (
        db_session.query(AuditLog)
        .filter(
            AuditLog.entity_type == "salary_record",
            AuditLog.entity_id == created_data["id"],
            AuditLog.action == "SALARY_CREATE",
        )
        .first()
    )
    assert audit is not None
    assert audit.change_data["reason"] == "PROMOTION"


def test_prevent_overlapping_salary_period(
    client: TestClient, auth_headers: dict, db_session: Session, temp_employee
):
    emp = temp_employee
    active_sal = next(s for s in emp.salary_records if s.effective_to is None)

    # Attempt to insert a record that starts BEFORE the current active salary's start date
    # and has open end date, which would conflict with existing periods
    conflicting_start = active_sal.effective_from - timedelta(days=10)
    response = client.post(
        f"/api/v1/employees/{emp.id}/salaries",
        headers=auth_headers,
        json={
            "amount": 90000,
            "currency": active_sal.currency,
            "effective_from": str(conflicting_start),
            "effective_to": None,
            "change_reason": "CONFLICTING_TEST",
        },
    )
    assert response.status_code == 400
    assert "overlaps" in response.json()["detail"].lower() or "overlapping" in response.json()["detail"].lower()


def test_salary_correction_updates_in_place_with_audit(
    client: TestClient, auth_headers: dict, db_session: Session, temp_employee
):
    emp = temp_employee
    active_sal = next(s for s in emp.salary_records if s.effective_to is None)
    corrected_amount = active_sal.amount + Decimal("2500.00")

    response = client.post(
        f"/api/v1/employees/{emp.id}/salaries",
        headers=auth_headers,
        json={
            "amount": float(corrected_amount),
            "currency": active_sal.currency,
            "effective_from": str(active_sal.effective_from),
            "change_reason": "CORRECTION",
            "is_correction": True,
            "correction_notes": "Corrected initial typo in offer letter",
        },
    )
    assert response.status_code == 201

    db_session.expire_all()
    corrected_rec = db_session.query(SalaryRecord).filter(SalaryRecord.id == active_sal.id).first()
    assert corrected_rec.amount == corrected_amount
    assert corrected_rec.is_correction is True
    assert corrected_rec.correction_notes == "Corrected initial typo in offer letter"

    # Verify audit log for correction
    audit = (
        db_session.query(AuditLog)
        .filter(
            AuditLog.entity_type == "salary_record",
            AuditLog.entity_id == active_sal.id,
            AuditLog.action == "SALARY_CORRECTION",
        )
        .first()
    )
    assert audit is not None
    assert audit.change_data["new"]["notes"] == "Corrected initial typo in offer letter"
