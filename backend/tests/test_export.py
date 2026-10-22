import csv
import io
from fastapi.testclient import TestClient


def test_export_employees_csv_streaming(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/reports/employees.csv?country_code=US", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment; filename=\"acme_employees_" in response.headers["content-disposition"]

    content = response.text
    reader = csv.reader(io.StringIO(content))
    header = next(reader)
    assert header == [
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
    ]

    first_row = next(reader)
    assert len(first_row) == 11
    # Country column is index 4
    assert first_row[4] == "US"
