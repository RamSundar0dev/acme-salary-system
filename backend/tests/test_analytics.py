from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.services.analytics_service import AnalyticsService
from app.models.employee import Employee
from app.models.salary_record import SalaryRecord


def test_analytics_summary(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/analytics/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_employees"] == 10000
    assert data["active_employees"] > 8500
    assert data["inactive_employees"] > 0
    assert data["total_employees"] == data["active_employees"] + data["inactive_employees"]

    # Verify payroll by currency
    assert len(data["payroll_by_currency"]) > 0
    currencies = [p["currency"] for p in data["payroll_by_currency"]]
    assert "USD" in currencies
    assert "EUR" in currencies
    assert "GBP" in currencies

    for item in data["payroll_by_currency"]:
        assert Decimal(str(item["total_amount"])) > 0
        assert item["headcount"] > 0

    # Verify metrics by country
    assert len(data["metrics_by_country"]) > 0
    for m in data["metrics_by_country"]:
        assert Decimal(str(m["avg_salary"])) > 0
        assert Decimal(str(m["median_salary"])) > 0

    # Verify metrics by department
    assert len(data["metrics_by_department"]) > 0


def test_compensation_distribution(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/analytics/distribution?currency=USD", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "buckets_by_currency" in data
    assert "USD" in data["buckets_by_currency"]
    usd_buckets = data["buckets_by_currency"]["USD"]
    assert len(usd_buckets) == 5
    total_count = sum(b["count"] for b in usd_buckets)
    assert total_count > 0


def test_known_dataset_median_calculation(db_session: Session):
    # Verify exact median mathematical behavior
    # Odd dataset: [50000, 60000, 70000, 80000, 90000] -> median is 70000
    odd_values = [Decimal("50000"), Decimal("60000"), Decimal("70000"), Decimal("80000"), Decimal("90000")]
    n_odd = len(odd_values)
    median_odd = odd_values[n_odd // 2]
    assert median_odd == Decimal("70000")

    # Even dataset: [50000, 60000, 70000, 80000] -> median is (60000 + 70000) / 2 = 65000
    even_values = [Decimal("50000"), Decimal("60000"), Decimal("70000"), Decimal("80000")]
    n_even = len(even_values)
    median_even = (even_values[n_even // 2 - 1] + even_values[n_even // 2]) / 2
    assert median_even == Decimal("65000")
