from decimal import Decimal
from typing import Dict, List, Optional
from pydantic import BaseModel


class CurrencyPayrollSummary(BaseModel):
    currency: str
    total_amount: Decimal
    headcount: int


class MetricByDimension(BaseModel):
    dimension: str
    currency: str
    employee_count: int
    total_payroll: Decimal
    avg_salary: Decimal
    median_salary: Decimal


class DistributionBucket(BaseModel):
    range_label: str
    currency: str
    min_amount: Decimal
    max_amount: Decimal
    count: int


class RecentSalaryChange(BaseModel):
    id: int
    employee_id: int
    employee_number: str
    employee_name: str
    old_amount: Optional[Decimal] = None
    new_amount: Decimal
    currency: str
    effective_from: str
    change_reason: str
    is_correction: bool
    changed_by_name: Optional[str] = None
    created_at: str


class DashboardSummaryResponse(BaseModel):
    total_employees: int
    active_employees: int
    inactive_employees: int
    payroll_by_currency: List[CurrencyPayrollSummary]
    metrics_by_country: List[MetricByDimension]
    metrics_by_department: List[MetricByDimension]
    recent_changes: List[RecentSalaryChange] = []


class DistributionResponse(BaseModel):
    buckets_by_currency: Dict[str, List[DistributionBucket]]
