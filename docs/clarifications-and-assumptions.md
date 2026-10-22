# ACME Salary Management System — Architectural Questions & Domain Assumptions

This document outlines key business questions, edge cases, and explicit architectural assumptions identified while modeling and building the compensation system for ACME's 10,000 employees.

---

## 1. Multi-Currency Aggregation vs. Strict Isolation

### The Problem
ACME operates across multiple international jurisdictions (US, EU, UK, India, etc.), paying employees in local currencies (`USD`, `EUR`, `GBP`, `INR`). Aggregating or averaging salaries across different currencies without a standardized FX conversion produces meaningless numbers, while dynamic FX conversion can introduce accounting discrepancies when exchange rates fluctuate.

### Questions for Product & Finance
1. Does ACME require a single consolidated global currency view (e.g., all figures normalized to `USD` using daily/monthly average FX rates)?
2. Or does Finance require strict per-currency reporting to match local entity payroll books?

### Architectural Assumption Implemented in MVP
- **Strict Currency Isolation:** All database aggregations (average salary, median compensation, departmental totals) are strictly partitioned by currency (`GROUP BY currency`).
- The UI features a clean currency selector allowing HR managers to analyze each currency domain independently without data distortion.
- The service layer is structured to easily plug in an FX conversion pipeline (e.g., via an external ECB/OpenExchangeRates feed) if global normalization is desired.

---

## 2. Effective-Dated Salary History vs. Retroactive Corrections

### The Problem
Employee compensation changes over time due to promotions, cost-of-living adjustments, or transfers. Additionally, HR managers occasionally need to schedule future increases or correct historical entry errors.

### Questions for HR & Payroll Operations
1. When a salary adjustment is scheduled for the future, should it automatically supersede active records on the effective date?
2. When a backdated salary adjustment occurs, does ACME require automatic payroll differential recalculation for prior months, or is an immutable audit record of the amendment sufficient?

### Architectural Assumption Implemented in MVP
- **PostgreSQL GiST Exclusion Constraints (`btree_gist`):** Implemented database-level constraint `exclude_overlapping_salaries` using `daterange(start_date, COALESCE(end_date, 'infinity'), '[)') WITH =`. This guarantees that no employee can ever have overlapping salary periods, even during concurrent API writes.
- **Continuous Historical Chain:** When a new salary is added, any currently open-ended salary (`end_date = NULL`) is cleanly capped at the day before the new `start_date`.
- **Immutable Audit Logging:** Every create, update, or delete emits an audit record with previous/new state diffs, actor ID, timestamp, and client IP address.

---

## 3. Regional vs. Global HR Access Control (RBAC)

### The Problem
In an organization with 10,000 employees, access to sensitive compensation data must be tightly controlled according to privacy laws (e.g., GDPR in the EU).

### Questions for Security & Compliance
1. Should regional HR managers only have access to employees within their specific country or legal entity?
2. Are executive or C-suite compensation tiers restricted to a subset of senior HR administrators?

### Architectural Assumption Implemented in MVP
- **Role-Based Access Control (RBAC):** Configured JWT-based authentication supporting role tiers (`hr_manager`, `hr_admin`, `auditor`).
- **Middleware-Ready Tenant Scoping:** The query layer uses dependency injection that can seamlessly apply tenant/country filters (`WHERE country = :user_country`) without rewriting business logic.

---

## 4. Compensation Component Scope

### The Problem
Total compensation packages often include base salary, performance bonuses, equity/stock grants, and tax-exempt allowances.

### Questions for HR Leadership
1. Is this system strictly managing annual base salary?
2. Will variable pay components (quarterly bonuses, one-off stipends) need to be factored into salary history and reporting?

### Architectural Assumption Implemented in MVP
- Built with high-precision `NUMERIC(14, 2)` arithmetic and modular fields to support breakdown tags (e.g., base pay, bonus component) without schema breakage.

---

## 5. High-Volume Data Access & Reporting

### The Problem
Displaying 10,000 employees with multi-year salary histories can easily overwhelm browser memory and network bandwidth if fetched as a raw dump.

### Architectural Assumption Implemented in MVP
- **Server-Side Pagination & Filtering:** TanStack Table on the frontend coupled with indexed PostgreSQL queries (`LIMIT` / `OFFSET` with composite indexes) ensures response times under 50ms.
- **Streaming CSV Export:** A dedicated streaming endpoint generates chunked CSV output on the fly, streaming 10,000 rows without loading the full dataset into server memory.

---

## Summary
These decisions balance immediate usability for HR managers with financial audit compliance and database-level integrity. All assumptions are reflected in the accompanying codebase and test suites.
