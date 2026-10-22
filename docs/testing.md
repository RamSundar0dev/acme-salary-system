# ACME Employee Salary Management System - Testing Strategy

## 1. Testing Philosophy & Pyramid
Our testing strategy ensures complete verification across all layers:
1. **Unit Tests:** Fast, isolated testing of business rules (salary positive check, currency validation, effective date logic, overlap prevention, median calculation).
2. **Integration Tests:** FastAPI test client testing route handlers, SQLAlchemy transactions, Alembic migrations, database constraints, and audit logging against a real database.
3. **Frontend Component & Hook Tests:** Vitest and React Testing Library verifying table pagination, sorting, form validation, error states, and auth redirection.
4. **End-to-End Tests:** Browser subagent and Playwright flows executing the complete HR manager user journey.

## 2. Test Execution Commands

### Backend Tests
```bash
# Set path to tools and run pytest
cd backend
pytest -v
# Run with coverage
pytest --cov=app tests/
```

### Frontend Tests
```bash
cd frontend
npm run test
# Run with coverage
npm run test:coverage
```

### End-to-End Tests
```bash
cd frontend
npx playwright test
```

## 3. Specific Test Matrix

| Area | Test Suite | What is Covered |
|------|------------|-----------------|
| **Salary Logic** | `test_salary_rules.py` | Positive decimals, invalid currency rejection, date period ordering, overlap prevention, closing current salary period. |
| **Median & Metrics** | `test_analytics.py` | Exact median calculations against controlled datasets (even & odd counts), currency group isolation, country & department filters. |
| **Audit Trail** | `test_audit.py` | Transactional rollback verification (if audit fails, salary change rolls back), change metadata schema, non-empty reason validation. |
| **Authentication** | `test_auth.py` | Login with valid credentials, rejection of bad passwords, token verification, role enforcement, unauthorized request blocking. |
| **Employee Directory** | `test_employees.py` | Server-side pagination, search by name/number/email, country/department filters, invalid pagination bounds. |
| **CSV Export** | `test_export.py` | Filter preservation, streaming response headers, CSV format correctness, sanitized values. |
| **Seed Verification** | `test_seed_count.py` | Asserts exactly 10,000 employees are present in the database with valid unique numbers and current salaries. |
