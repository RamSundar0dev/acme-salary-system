from fastapi.testclient import TestClient


def test_list_employees_pagination(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/employees?page=1&page_size=20", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 10000
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert len(data["items"]) == 20
    assert data["total_pages"] == 500

    # Verify first item contains expected fields
    item = data["items"][0]
    assert "employee_number" in item
    assert "department_name" in item
    assert "current_salary" in item
    assert "currency" in item


def test_list_employees_page_size_enforced(client: TestClient, auth_headers: dict):
    # If client requests 200 records, max 100 is enforced
    response = client.get("/api/v1/employees?page=1&page_size=200", headers=auth_headers)
    assert response.status_code == 422  # validation rejected > 100


def test_search_employee_by_number(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/employees?search=ACM-000042", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(emp["employee_number"] == "ACM-000042" for emp in data["items"])


def test_filter_employee_by_country_and_status(client: TestClient, auth_headers: dict):
    response = client.get(
        "/api/v1/employees?country_code=US&employment_status=ACTIVE&page_size=10",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    for emp in data["items"]:
        assert emp["country_code"] == "US"
        assert emp["employment_status"] == "ACTIVE"


def test_get_employee_detail(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/employees/1", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "salary_history" in data
    assert len(data["salary_history"]) >= 1
    assert "department" in data
    assert "name" in data["department"]
