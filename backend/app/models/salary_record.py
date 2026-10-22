from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    String,
    Date,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class SalaryRecord(Base):
    __tablename__ = "salary_records"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(3), nullable=False, index=True)  # ISO 4217 code
    effective_from = Column(Date, nullable=False, index=True)
    effective_to = Column(Date, nullable=True, index=True)
    change_reason = Column(String(100), nullable=False)
    is_correction = Column(Boolean, nullable=False, default=False)
    correction_notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    employee = relationship("Employee", back_populates="salary_records")
    creator = relationship("User")

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_positive_salary"),
        CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name="check_valid_salary_period",
        ),
        Index("idx_salaries_emp_effective", "employee_id", "effective_from"),
    )
