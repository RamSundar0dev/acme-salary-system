# ACME Employee Salary Management System - Security & Compliance

## 1. Threat Model & Asset Sensitivity
- **Primary Asset:** Employee compensation history and personally identifiable information (PII).
- **Core Threats:** Unauthorized access to compensation data, tampering with salary history, credential compromise, leakage through application logging or error stack traces, SQL injection, and CSRF attacks.

## 2. Authentication & Authorization Architecture
- **Password Security:** Passwords are never stored in plaintext. Hashing is performed using `bcrypt` with automatic salting (cost factor 12).
- **Session & Token Management:**
  - Standard JSON Web Tokens (JWT) signed with HMAC-SHA256 (`HS256`) using a strong 256-bit server secret key.
  - Configurable expiration (default: 8 hours).
  - Auth tokens are transmitted via `Authorization: Bearer <token>` or HTTP-only, secure, `SameSite=Lax` cookies.
- **Server-side Authorization:**
  - Every API endpoint under `/api/v1` (except health and login) is gated by FastAPI dependency `get_current_active_user`.
  - Roles: `hr_manager`, `admin`. Non-authenticated or non-admin requests receive `401 Unauthorized` or `403 Forbidden`.

## 3. Data Protection in Logs & Errors
- **Log Sanitization:** Application loggers explicitly filter out raw request bodies on auth and salary endpoints. No compensation amounts, tokens, or plaintext passwords ever appear in stdout or disk logs.
- **Error Sanitization:** Unhandled 500 exceptions produce an obfuscated error response (`{"detail": "Internal server error", "request_id": "..."}`) to prevent database schema exposure, stack traces, or internal IP disclosure. Detailed exceptions are recorded in private server diagnostics only.

## 4. Audit Logging & Non-Repudiation
- All salary modifications (creation, updates, corrections) are logged in the `audit_logs` table.
- Transactions are atomic: if the audit log insert fails, the entire salary change is rolled back.
- `audit_logs` is append-only by application design. No update or delete endpoints exist for audit records.
- Stored audit metadata includes:
  - Actor User ID
  - Action type (`SALARY_CREATE`, `SALARY_UPDATE`, `SALARY_CORRECTION`)
  - Entity ID and Type
  - Before/After values diff (sanitized, excluding passwords/tokens)
  - Change reason provided by the HR manager
  - UTC timestamp

## 5. SQL Injection & Parameter Tampering Safeguards
- All database interactions use SQLAlchemy 2.0 parameterized queries. Zero string concatenation or f-strings in SQL execution.
- Sorting columns are validated against a strict whitelist enum (`id`, `employee_number`, `last_name`, `created_at`). Client-specified arbitrary SQL column names are rejected with `422 Unprocessable Entity`.

## 6. Secure Administrator Bootstrap
- An initial HR Manager account is created deterministically via a dedicated CLI command:
  ```bash
  python -m app.scripts.bootstrap_admin --email hr.manager@acme.corp --password InitialSecurePass123!
  ```
- Or via environment variables `ADMIN_EMAIL` and `ADMIN_INITIAL_PASSWORD` during seed operations.
- Default fallback credentials are never exposed in client bundles or public endpoints.
