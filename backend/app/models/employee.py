from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.session import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_number = Column(String(30), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    country_code = Column(String(2), nullable=False, index=True)  # ISO 3166-1 alpha-2
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    employment_status = Column(String(30), nullable=False, default="ACTIVE", index=True)
    employment_start_date = Column(Date, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    department = relationship("Department", back_populates="employees")
    salary_records = relationship(
        "SalaryRecord",
        back_populates="employee",
        cascade="all, delete-orphan",
        order_by="desc(SalaryRecord.effective_from)",
    )

    __table_args__ = (
        Index("idx_employees_country_dept_status", "country_code", "department_id", "employment_status"),
        Index("idx_employees_last_first_name", "last_name", "first_name"),
    )
