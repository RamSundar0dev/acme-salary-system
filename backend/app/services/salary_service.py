from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.salary_record import SalaryRecord
from app.models.user import User
from app.schemas.salary import SalaryCreate, SalaryResponse
from app.services.audit_service import AuditService


class SalaryService:
    @staticmethod
    def get_salary_history(db: Session, employee_id: int) -> List[SalaryRecord]:
        return (
            db.query(SalaryRecord)
            .filter(SalaryRecord.employee_id == employee_id)
            .order_by(SalaryRecord.effective_from.desc())
            .all()
        )

    @staticmethod
    def get_current_salary(
        db: Session, employee_id: int, as_of_date: Optional[date] = None
    ) -> Optional[SalaryRecord]:
        target_date = as_of_date or date.today()
        # Find record where target_date >= effective_from and (effective_to IS NULL or target_date < effective_to)
        return (
            db.query(SalaryRecord)
            .filter(
                SalaryRecord.employee_id == employee_id,
                SalaryRecord.effective_from <= target_date,
                or_(
                    SalaryRecord.effective_to.is_(None),
                    SalaryRecord.effective_to > target_date,
                ),
            )
            .order_by(SalaryRecord.effective_from.desc())
            .first()
        )

    @staticmethod
    def record_salary_change(
        db: Session,
        employee_id: int,
        salary_data: SalaryCreate,
        current_user: User,
        ip_address: Optional[str] = None,
    ) -> SalaryRecord:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee {employee_id} not found",
            )

        # Handle correction of current record
        if salary_data.is_correction:
            current_active = (
                db.query(SalaryRecord)
                .filter(
                    SalaryRecord.employee_id == employee_id,
                    SalaryRecord.effective_to.is_(None),
                )
                .first()
            )
            if current_active:
                old_data = {
                    "id": current_active.id,
                    "amount": str(current_active.amount),
                    "currency": current_active.currency,
                    "effective_from": str(current_active.effective_from),
                    "change_reason": current_active.change_reason,
                }
                # Update current active record in-place with audit provenance
                current_active.amount = salary_data.amount
                current_active.currency = salary_data.currency
                current_active.effective_from = salary_data.effective_from
                current_active.change_reason = salary_data.change_reason
                current_active.is_correction = True
                current_active.correction_notes = salary_data.correction_notes

                AuditService.log_action(
                    db=db,
                    actor=current_user,
                    action="SALARY_CORRECTION",
                    entity_type="salary_record",
                    entity_id=current_active.id,
                    change_data={
                        "employee_id": employee_id,
                        "old": old_data,
                        "new": {
                            "amount": str(salary_data.amount),
                            "currency": salary_data.currency,
                            "effective_from": str(salary_data.effective_from),
                            "notes": salary_data.correction_notes,
                        },
                    },
                    ip_address=ip_address,
                )
                try:
                    db.commit()
                    db.refresh(current_active)
                    return current_active
                except IntegrityError as e:
                    db.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Database constraint violation during correction: {str(e)}",
                    )

        # Standard Salary Change Workflow
        # 1. Check for overlapping records in the proposed date range
        new_from = salary_data.effective_from
        new_to = salary_data.effective_to

        # Query existing records for this employee
        existing_records = (
            db.query(SalaryRecord)
            .filter(SalaryRecord.employee_id == employee_id)
            .all()
        )

        for rec in existing_records:
            rec_from = rec.effective_from
            rec_to = rec.effective_to  # None means infinity

            # Check overlap between [new_from, new_to) and [rec_from, rec_to)
            # If rec is the open-ended current salary and new_from > rec_from,
            # we will automatically cap rec.effective_to = new_from
            if rec_to is None and new_from > rec_from and new_to is None:
                # Normal promotion / salary increase flow
                rec.effective_to = new_from
                continue

            # Standard interval overlap test: startA < endB and startB < endA
            # with open-ended intervals treated as infinity
            overlaps = True
            if new_to is not None and new_to <= rec_from:
                overlaps = False
            if rec_to is not None and rec_to <= new_from:
                overlaps = False

            if overlaps:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Overlapping salary period: Proposed effective period [{new_from} to {new_to or 'open'}) "
                        f"overlaps with existing record #{rec.id} [{rec_from} to {rec_to or 'open'}). "
                        "ACME business rules require non-overlapping compensation periods."
                    ),
                )

        new_record = SalaryRecord(
            employee_id=employee_id,
            amount=salary_data.amount,
            currency=salary_data.currency,
            effective_from=salary_data.effective_from,
            effective_to=salary_data.effective_to,
            change_reason=salary_data.change_reason,
            is_correction=False,
            correction_notes=salary_data.correction_notes,
            created_by=current_user.id,
        )
        db.add(new_record)
        db.flush()  # assign ID to new_record

        AuditService.log_action(
            db=db,
            actor=current_user,
            action="SALARY_CREATE",
            entity_type="salary_record",
            entity_id=new_record.id,
            change_data={
                "employee_id": employee_id,
                "amount": str(new_record.amount),
                "currency": new_record.currency,
                "effective_from": str(new_record.effective_from),
                "effective_to": str(new_record.effective_to) if new_record.effective_to else None,
                "reason": new_record.change_reason,
            },
            ip_address=ip_address,
        )

        try:
            db.commit()
            db.refresh(new_record)
            return new_record
        except IntegrityError as exc:
            db.rollback()
            err_msg = str(exc)
            if "exclude_overlapping_salaries" in err_msg or "conflicting key" in err_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Database constraint prevented overlapping salary period for this employee.",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database integrity error: {err_msg}",
            )
