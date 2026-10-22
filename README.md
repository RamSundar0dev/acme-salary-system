# ACME Employee Salary Management System

[![CI Pipeline](https://github.com/acme/salary-system/actions/workflows/ci.yml/badge.svg)](https://github.com/acme/salary-system)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16.1-blue.svg)](https://www.postgresql.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.124-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue.svg)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38bdf8.svg)](https://tailwindcss.com/)

A complete, production-minded Employee Salary Management System built for **ACME Corp**, managing compensation for **10,000 employees** across multiple countries and departments.

Built as an engineering assessment for **Incubyte**.

---

## 1. Key Highlights & Architectural Strengths

- **Scale & Real Dataset:** Authoritative PostgreSQL 16 database pre-seeded with **exactly 10,000 synthetic employees** and full compensation histories (~13,000 records).
- **Zero Binary Floating-Point:** All salary computations utilize fixed-precision `NUMERIC(14, 2)` / Python `Decimal`.
- **Effective-Dating Semantics:** Inclusive start `[effective_from` and exclusive end `, effective_to)`. No historical overwrites.
- **PostgreSQL Exclusion Constraints:** Mathematical impossibility of overlapping salary periods via `btree_gist` / `EXCLUDE USING gist`.
- **Currency Isolation:** Currency sums (USD, EUR, GBP, CAD, INR, AUD, SGD, JPY) are strictly grouped and never arbitrarily combined without verified FX rates.
- **In-Database Aggregations:** Computes headcounts, sums, averages, and exact medians (`percentile_cont(0.5)`) in < 50ms without loading 10,000 rows into application memory.
- **Server-Side Pagination:** TanStack table with indexed search across names, emails, and IDs, bounded to 15-100 items per page.
- **Streaming CSV Export:** Memory-conscious chunked HTTP streaming for filtered employee reports.
- **Transactional Audit Trail:** Every salary change or correction commits an atomic, structured audit log.
- **Security:** bcrypt password hashing, JWT bearer auth with HTTP-only cookies, sanitized error and log output.

---

## 2. Technology Stack

### Backend
- **Python 3.8+ / 3.11**
- **FastAPI**: Asynchronous REST API framework
- **SQLAlchemy 2.0**: Modern ORM and Core SQL builder
- **Alembic**: Database schema migrations
- **PostgreSQL 16**: Authoritative relational data store with `btree_gist`
- **Pydantic v2**: Request & response validation
- **Pytest**: Automated test suite (23 unit & integration tests)

### Frontend
- **Next.js 14** (App Router)
- **TypeScript** with strict type checking
- **Tailwind CSS** & **shadcn/ui** design system
- **TanStack Table**: Server-side pagination and sorting
- **Recharts**: Compensation distribution and department comparison charts
- **Lucide React**: Enterprise icons
- **Vitest & React Testing Library**: Component & utility testing

---

## 3. Quick Start & Local Development

### Prerequisites
- Python 3.8+ or Python 3.11
- Node.js 20+ and npm
- PostgreSQL 16 (or Docker)

### Option A: Running with Docker Compose (Recommended)
```bash
# Clone the repository
git clone <repo-url>
cd acme-salary-system

# Start PostgreSQL, Backend, and Frontend containers
docker-compose up -d

# Seed the database with 10,000 employees
docker-compose exec backend python -m app.scripts.seed --reset

# Open the application
# Frontend: http://localhost:3000
# Backend API Docs: http://localhost:8000/docs
```

### Option B: Running Locally

#### 1. Setup Backend & PostgreSQL
```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (.env)
cp ../.env.example .env

# Run database migrations
alembic upgrade head

# Seed exactly 10,000 employees + bootstrap HR admin
python -m app.scripts.seed --reset

# Start FastAPI server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### 2. Setup Frontend
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
# Application opens on http://localhost:3000
```

---

## 4. Default Credentials (HR Manager)

| Role | Email | Password |
|------|-------|----------|
| **HR Manager** | `hr.manager@acme.corp` | `AcmeHR2026!SecurePass` |

*Note: Initial administrator is created securely via `app.scripts.bootstrap_admin` or during the seed operation.*

---

## 5. Running Automated Tests

### Backend Test Suite (Pytest)
```bash
cd backend
pytest -v
```
Covers:
- Positive salary and ISO 4217 currency validation
- Effective date ordering and boundary rules
- Prevention of overlapping salary periods
- Automatic closing of active salary records
- Salary correction in-place with audit logging
- Known dataset exact median calculations (odd & even)
- Server-side employee search and pagination
- Streaming CSV report filtering
- Exact 10,000 employee seed count assertion

### Frontend Test Suite (Vitest)
```bash
cd frontend
npm run test
```

---

## 6. Project Documentation Artifacts

- [docs/requirements.md](docs/requirements.md): Concise product requirements and business scope
- [docs/architecture.md](docs/architecture.md): Request flows, sequence diagrams, and system architecture
- [docs/data-model.md](docs/data-model.md): Database tables, relationships, constraints, and audit semantics
- [docs/tradeoffs.md](docs/tradeoffs.md): Decisions, alternatives evaluated, and rationales
- [docs/performance.md](docs/performance.md): Indexing, database aggregation strategy, and pagination
- [docs/security.md](docs/security.md): Authentication, authorization, log sanitization, and secrets
- [docs/testing.md](docs/testing.md): Testing pyramid, coverage matrix, and test commands
- [docs/demo-script.md](docs/demo-script.md): 5-minute evaluation walkthrough script
- [docs/ai-workflow.md](docs/ai-workflow.md): AI agent prompts, engineering decisions, and verification log

---

## 7. License
Proprietary & Confidential - ACME Corp & Incubyte Assessment.
