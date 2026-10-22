# ACME Employee Salary Management System - Product Requirements

## 1. Executive Summary & Objective
ACME is a multinational enterprise with 10,000 employees distributed across multiple countries and departments. The historical compensation workflow depended on error-prone, disconnected Excel spreadsheets. This system replaces that manual workflow with a centralized, secure, highly performant web-based application specifically designed for HR Managers and leadership to manage compensation, view organizational analytics, and audit changes.

## 2. User Persona & Scope
- **Primary Persona:** HR Manager (authorized administrator with compensation management and reporting privileges).
- **Scale:** 10,000 active and historical employee records across multiple currencies (USD, EUR, GBP, CAD, INR, AUD, SGD, JPY).
- **Compliance:** Strict audit trail of salary changes, zero silent overwrites, isolation of sensitive salary data from application logs and unauthorized users.

## 3. Functional Requirements

### A. HR Executive Analytics Dashboard
- **Key Metrics:** Total employee count, active vs. inactive counts, currency-isolated total payroll sums.
- **Aggregations:** Average and median salary grouped by country and department.
- **Visualizations:** Compensation distribution histogram/ranges, employee count distributions by geography and department.
- **Filtering:** Dynamic filtering by Country, Department, Employment Status, and Currency.
- **Audit Feed:** Recent salary modifications visible only to authorized HR managers.
- **Rule on Currencies:** No currency conversion without documented rate sources. Payroll totals are strictly separated by ISO 4217 currency.

### B. Scalable Employee Directory (10,000 Records)
- **Server-side Pagination & Limits:** Validated page parameters (default 15, max 100), total record counts, page jumping.
- **Multi-parameter Search:** Server-side search across Employee Number, First Name, Last Name, and Work Email.
- **Faceted Filtering:** Country code, Department ID, and Employment Status (Active, Terminated, On Leave).
- **Sorting:** Safe column sorting on Employee Number, Name, Department, Country, and Current Salary.
- **Performance:** Sub-second response times on 10,000 records using database indexes.

### C. Employee Compensation Profile & History
- **Employee Identity:** Unique employee number (e.g., `ACM-001001`), full name, work email, department, country, start date, status.
- **Effective Compensation:** Current effective salary as of the target date with ISO 4217 currency code.
- **Salary History Timeline:** Complete chronological record of every compensation period with `effective_from` (inclusive) and `effective_to` (exclusive or null for current).
- **Audit Attribution:** Who created/modified the record, timestamp (UTC), change type (New Hire, Merit Increase, Promotion, Market Adjustment, Correction), and reason.

### D. Salary Management & Business Rules
1. **Positive Fixed-Precision Values:** Salary amounts must be positive `NUMERIC(14, 2)`. Floating-point arithmetic is strictly prohibited.
2. **ISO 4217 Currency:** Must match validated organizational currencies (USD, EUR, GBP, CAD, INR, AUD, SGD, JPY).
3. **Effective Period Semantics:** Periods have inclusive start `[effective_from` and exclusive end `, effective_to)`.
4. **No Overlapping Records:** An employee cannot have overlapping salary periods. When a new salary is recorded with an effective date:
   - If a current active salary exists (`effective_to IS NULL`), its `effective_to` is automatically adjusted to the new record's `effective_from`.
   - Overlaps are strictly prevented via PostgreSQL exclusion constraints (`EXCLUDE USING gist`) and application validation.
5. **Legitimate Changes vs. Corrections:**
   - *Legitimate Salary Change:* Creates a new effective-dated record, closing the previous one.
   - *Correction:* Explicit correction flag/audit note for fixing human data entry errors without destroying historical provenance.
6. **Transactional Audit Logging:** Every salary creation, update, or correction writes an atomic audit record in the same database transaction.

### E. Reporting & CSV Export
- Server-side filtered CSV export of employees with current salary, department, and country.
- Streaming/memory-conscious generation to prevent memory spikes on large exports.

### F. Security & Access Control
- JWT or secure HTTP-only session cookie authentication for HR Managers.
- Passwords hashed using bcrypt / Argon2.
- Server-side role enforcement on every API endpoint.
- Sanitized logs: Zero salary values, tokens, or PII in general application logs.
- Bootstrapped admin CLI/seed command with secure configuration.
