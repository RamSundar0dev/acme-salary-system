from decimal import Decimal
from typing import Dict, List, Optional
from sqlalchemy import func, text, or_
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.department import Department
from app.models.salary_record import SalaryRecord
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.analytics import (
    DashboardSummaryResponse,
    CurrencyPayrollSummary,
    MetricByDimension,
    DistributionResponse,
    DistributionBucket,
    RecentSalaryChange,
)


class AnalyticsService:
    @staticmethod
    def get_dashboard_summary(
        db: Session,
        country_code: Optional[str] = None,
        department_id: Optional[int] = None,
        currency: Optional[str] = None,
    ) -> DashboardSummaryResponse:
        # Base filter conditions for employees
        emp_filter = []
        if country_code:
            emp_filter.append(Employee.country_code == country_code.upper())
        if department_id:
            emp_filter.append(Employee.department_id == department_id)

        # Total counts
        total_employees = db.query(Employee).filter(*emp_filter).count()
        active_employees = (
            db.query(Employee)
            .filter(*emp_filter, Employee.employment_status == "ACTIVE")
            .count()
        )
        inactive_employees = total_employees - active_employees

        # Payroll totals grouped by currency (strictly isolated)
        payroll_query = (
            db.query(
                SalaryRecord.currency,
                func.sum(SalaryRecord.amount).label("total_amount"),
                func.count(Employee.id).label("headcount"),
            )
            .join(Employee, SalaryRecord.employee_id == Employee.id)
            .filter(
                SalaryRecord.effective_to.is_(None),
                Employee.employment_status == "ACTIVE",
                *emp_filter,
            )
        )
        if currency:
            payroll_query = payroll_query.filter(SalaryRecord.currency == currency.upper())

        payroll_rows = payroll_query.group_by(SalaryRecord.currency).all()

        payroll_by_currency = [
            CurrencyPayrollSummary(
                currency=r.currency,
                total_amount=Decimal(str(r.total_amount or 0)),
                headcount=r.headcount,
            )
            for r in payroll_rows
        ]

        # In-database Aggregation for Country & Department Metrics
        # Using PostgreSQL native percentile_cont(0.5) when on Postgres
        is_postgres = db.bind and db.bind.dialect.name == "postgresql"

        metrics_by_country = AnalyticsService._compute_dimension_metrics(
            db=db,
            dimension_col="country_code",
            is_postgres=is_postgres,
            emp_filter=emp_filter,
            currency_filter=currency,
        )

        metrics_by_department = AnalyticsService._compute_dimension_metrics(
            db=db,
            dimension_col="department_name",
            is_postgres=is_postgres,
            emp_filter=emp_filter,
            currency_filter=currency,
        )

        # Recent salary changes (latest 10)
        recent_changes = AnalyticsService._get_recent_salary_changes(db, limit=10)

        return DashboardSummaryResponse(
            total_employees=total_employees,
            active_employees=active_employees,
            inactive_employees=inactive_employees,
            payroll_by_currency=payroll_by_currency,
            metrics_by_country=metrics_by_country,
            metrics_by_department=metrics_by_department,
            recent_changes=recent_changes,
        )

    @staticmethod
    def _compute_dimension_metrics(
        db: Session,
        dimension_col: str,
        is_postgres: bool,
        emp_filter: list,
        currency_filter: Optional[str] = None,
    ) -> List[MetricByDimension]:
        if dimension_col == "country_code":
            dim_expr = Employee.country_code
        else:
            dim_expr = Department.name

        base_q = (
            db.query(
                dim_expr.label("dimension"),
                SalaryRecord.currency,
                func.count(Employee.id).label("employee_count"),
                func.sum(SalaryRecord.amount).label("total_payroll"),
                func.avg(SalaryRecord.amount).label("avg_salary"),
            )
            .join(Department, Employee.department_id == Department.id)
            .join(
                SalaryRecord,
                (SalaryRecord.employee_id == Employee.id)
                & (SalaryRecord.effective_to.is_(None)),
            )
            .filter(Employee.employment_status == "ACTIVE", *emp_filter)
        )

        if currency_filter:
            base_q = base_q.filter(SalaryRecord.currency == currency_filter.upper())

        rows = (
            base_q.group_by(dim_expr, SalaryRecord.currency)
            .order_by(dim_expr, SalaryRecord.currency)
            .all()
        )

        results = []
        for r in rows:
            # Compute exact median
            median_val = Decimal("0")
            if is_postgres:
                # Use PostgreSQL percentile_cont(0.5)
                dim_where = f"e.country_code = '{r.dimension}'" if dimension_col == "country_code" else f"d.name = '{r.dimension}'"
                sql = text(f"""
                    SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY s.amount)
                    FROM employees e
                    JOIN departments d ON e.department_id = d.id
                    JOIN salary_records s ON s.employee_id = e.id AND s.effective_to IS NULL
                    WHERE e.employment_status = 'ACTIVE'
                      AND {dim_where}
                      AND s.currency = :curr
                """)
                res = db.execute(sql, {"curr": r.currency}).scalar()
                if res is not None:
                    median_val = round(Decimal(str(res)), 2)
            else:
                # Fallback for SQLite in unit tests
                sub_q = (
                    db.query(SalaryRecord.amount)
                    .join(Employee, SalaryRecord.employee_id == Employee.id)
                    .join(Department, Employee.department_id == Department.id)
                    .filter(
                        Employee.employment_status == "ACTIVE",
                        SalaryRecord.effective_to.is_(None),
                        SalaryRecord.currency == r.currency,
                        (Employee.country_code == r.dimension) if dimension_col == "country_code" else (Department.name == r.dimension),
                    )
                    .order_by(SalaryRecord.amount)
                    .all()
                )
                vals = [x[0] for x in sub_q]
                if vals:
                    n = len(vals)
                    if n % 2 == 1:
                        median_val = Decimal(str(vals[n // 2]))
                    else:
                        median_val = Decimal(str((vals[n // 2 - 1] + vals[n // 2]) / 2))

            results.append(
                MetricByDimension(
                    dimension=str(r.dimension),
                    currency=r.currency,
                    employee_count=r.employee_count,
                    total_payroll=Decimal(str(r.total_payroll or 0)),
                    avg_salary=round(Decimal(str(r.avg_salary or 0)), 2),
                    median_salary=median_val,
                )
            )
        return results

    @staticmethod
    def get_compensation_distribution(
        db: Session,
        currency_filter: Optional[str] = None,
    ) -> DistributionResponse:
        # Standard salary tiers (in thousands): <50k, 50k-80k, 80k-110k, 110k-150k, >150k
        tiers = [
            ("< 50k", Decimal("0"), Decimal("50000")),
            ("50k - 80k", Decimal("50000"), Decimal("80000")),
            ("80k - 110k", Decimal("80000"), Decimal("110000")),
            ("110k - 150k", Decimal("110000"), Decimal("150000")),
            ("> 150k", Decimal("150000"), Decimal("99999999")),
        ]

        # Group by currency
        curr_query = (
            db.query(SalaryRecord.currency)
            .filter(SalaryRecord.effective_to.is_(None))
            .distinct()
        )
        if currency_filter:
            curr_query = curr_query.filter(SalaryRecord.currency == currency_filter.upper())
        currencies = [c[0] for c in curr_query.all()]

        buckets_map: Dict[str, List[DistributionBucket]] = {}

        for curr in currencies:
            curr_buckets = []
            for label, min_amt, max_amt in tiers:
                q = (
                    db.query(func.count(SalaryRecord.id))
                    .join(Employee, SalaryRecord.employee_id == Employee.id)
                    .filter(
                        SalaryRecord.effective_to.is_(None),
                        SalaryRecord.currency == curr,
                        Employee.employment_status == "ACTIVE",
                        SalaryRecord.amount >= min_amt,
                        SalaryRecord.amount < max_amt,
                    )
                )
                count = q.scalar() or 0
                curr_buckets.append(
                    DistributionBucket(
                        range_label=label,
                        currency=curr,
                        min_amount=min_amt,
                        max_amount=max_amt,
                        count=count,
                    )
                )
            buckets_map[curr] = curr_buckets

        return DistributionResponse(buckets_by_currency=buckets_map)

    @staticmethod
    def _get_recent_salary_changes(db: Session, limit: int = 10) -> List[RecentSalaryChange]:
        # Fetch latest audit logs for salary_record
        logs = (
            db.query(AuditLog)
            .filter(AuditLog.entity_type == "salary_record")
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )
        changes = []
        for l in logs:
            data = l.change_data or {}
            emp_id = data.get("employee_id")
            if not emp_id:
                # Try finding from salary record
                s_rec = db.query(SalaryRecord).filter(SalaryRecord.id == l.entity_id).first()
                emp_id = s_rec.employee_id if s_rec else None

            emp = db.query(Employee).filter(Employee.id == emp_id).first() if emp_id else None
            emp_num = emp.employee_number if emp else "N/A"
            emp_name = f"{emp.first_name} {emp.last_name}" if emp else "Unknown"

            old_amt = None
            if "old" in data and isinstance(data["old"], dict) and "amount" in data["old"]:
                old_amt = Decimal(str(data["old"]["amount"]))

            new_amt = Decimal(str(data.get("amount") or (data.get("new", {}) or {}).get("amount", "0")))
            curr = str(data.get("currency") or (data.get("new", {}) or {}).get("currency", "USD"))
            eff_from = str(data.get("effective_from") or (data.get("new", {}) or {}).get("effective_from", ""))
            reason = str(data.get("reason") or l.action)

            actor = db.query(User).filter(User.id == l.actor_id).first() if l.actor_id else None
            actor_name = actor.full_name if actor else "System"

            changes.append(
                RecentSalaryChange(
                    id=l.id,
                    employee_id=emp_id or 0,
                    employee_number=emp_num,
                    employee_name=emp_name,
                    old_amount=old_amt,
                    new_amount=new_amt,
                    currency=curr,
                    effective_from=eff_from,
                    change_reason=reason,
                    is_correction=(l.action == "SALARY_CORRECTION"),
                    changed_by_name=actor_name,
                    created_at=l.created_at.isoformat(),
                )
            )
        return changes
