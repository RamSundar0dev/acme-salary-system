# ACME Employee Salary Management System - AI Workflow & Engineering Log

## 1. Objective & AI Collaboration Approach
This document transparently chronicles the AI agent workflow, engineering decisions, prompts, tool executions, and verification steps taken during the development of the ACME Salary Management System.

In accordance with the prompt's instructions:
- No fabricated AI records.
- Actual tools, real environment challenges, real errors encountered, and real resolutions are documented.

## 2. Environment Discovery & Toolchain Bootstrap

### Observation
- The host environment is Windows with PowerShell.
- Default system PATH initially lacked Node.js, Git, and Docker. Python 3.8 was available.
- `winget` installation of Git requested interactive UAC administrator elevation which was not possible non-interactively.
- `curl.exe` encountered Windows Schannel revocation check errors (`0x80092012`).

### AI Engineering Actions & Decisions
1. **Certificate Revocation Bypass:** Configured `--ssl-no-revoke` for automated downloads.
2. **Zero-Admin Portable Toolchain:** Downloaded portable distributions directly into a local `scratch/tools` directory:
   - Git for Windows MinGit (v2.44.0)
   - Node.js LTS (v20.18.0) + npm (10.8.2)
   - PostgreSQL 16.1 Windows x64 EnterpriseDB portable binaries
3. **Dedicated Python Virtual Environment:** Initialized isolated venv (`scratch/tools/venv`), upgraded pip, and pinned `psycopg2-binary==2.9.9` (which provides pre-built Windows x64 wheels for Python 3.8 without needing MSVC C++ compilation tools).
4. **Persistent PATH Configuration:** Configured a unified path prepend to ensure deterministic tool execution across all background tasks.
5. **Native PostgreSQL Instance:** Initialized database cluster with `initdb.exe` and started daemon with `pg_ctl.exe` on port 5432, creating the authoritative `acme_salary` database.

## 3. Incremental Implementation Milestones

- **Milestone 1: Discovery, Planning & Documentation**
  - Inspected workspace and environment tools.
  - Authored comprehensive documentation: `docs/requirements.md`, `docs/architecture.md`, `docs/data-model.md`, `docs/tradeoffs.md`, `docs/performance.md`, `docs/security.md`, `docs/testing.md`.
  - Initialized Git repository with clean commit history.

- **Milestone 2: Database Schema & Backend Foundation**
  - SQLAlchemy 2.0 ORM models for `User`, `Department`, `Employee`, `SalaryRecord`, `AuditLog`.
  - Alembic migrations setup and execution against real PostgreSQL 16.
  - Pydantic v2 schemas and validation logic.

- **Milestone 3: Core API Services & Business Logic**
  - Authentication (JWT + bcrypt).
  - Employee directory with indexed search, multi-faceted filtering, and server-side pagination.
  - Salary service enforcing positive decimals, currency validation, overlap prevention, period closing, and atomic audit logging.

- **Milestone 4: Deterministic 10,000 Employee Seed Script**
  - High-performance batch generation using deterministic random seed (`seed=42`).
  - Realistic multi-country, multi-department workforce with historical salary records.
  - Verification test asserting exact count = 10,000.

- **Milestone 5: Analytics & Export Engine**
  - In-database SQL aggregation for headcount, sum by currency, average, and median.
  - Streaming CSV export for filtered workforce data.

- **Milestone 6: Polished Next.js Frontend**
  - Clean enterprise dashboard with shadcn/ui components, Tailwind CSS, TanStack Table, Recharts.
  - Real API integration (zero mock data in production views).

- **Milestone 7: Comprehensive Verification & End-to-End Testing**
  - Full pytest backend suite.
  - Frontend component & integration tests.
  - Browser automation walkthrough and demo script.

## 4. Representative Prompts & Verification Patterns

### Backend Validation Testing Prompt Pattern
```text
Verify that an attempt to record an overlapping salary period for an employee raises
a 400/422 validation error and does not corrupt existing records or leave orphaned audit logs.
```

### PostgreSQL Aggregation Query Pattern
```text
Construct a single SQL aggregation using percentile_cont(0.5) WITHIN GROUP (ORDER BY amount)
and SUM(amount) GROUP BY currency to compute dashboard metrics in under 50ms without loading
records into application memory.
```
