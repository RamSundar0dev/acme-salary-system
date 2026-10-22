# ACME Employee Salary Management System - Architectural Tradeoffs

## 1. Effective-Dated Salary Design vs. Snapshot Overwrites

- **Option A (Chosen): Explicit Effective Dating with Closed Ranges `[from, to)`**
  - *Pros:* Preserves 100% of historical compensation without destructive updates. Allows retroactive analysis, auditing, and point-in-time compensation queries. Matches real enterprise ERP/HRIS standards (Workday, SAP SuccessFactors).
  - *Cons:* Requires interval overlap validation and updating the preceding record's `effective_to` when a new record begins.
  - *Decision:* Selected because compensation data requires high financial and legal audit integrity.

- **Option B: Simple Mutation with Audit Log Only**
  - *Pros:* Simpler schema with just `current_salary` on the employee table.
  - *Cons:* Hard to run point-in-time analytics (e.g. "What was Q2 payroll last year?"). Audit logs become the defacto store of state, leading to complex reconstructions.
  - *Rejected.*

## 2. PostgreSQL Exclusion Constraints vs. Application-Only Validation

- **Option A (Chosen): Database Exclusion Constraint (`EXCLUDE USING gist`) + Application Pre-check**
  - *Pros:* Concurrency-safe against race conditions when multiple HR admins update salaries simultaneously. Enforced at the engine level even if data is inserted via scripts or migrations.
  - *Cons:* Requires `btree_gist` extension in PostgreSQL.
  - *Decision:* Selected because data integrity on salaries must be mathematically ironclad.

- **Option B: Application-Only Validation**
  - *Pros:* Portable across all SQL engines including SQLite.
  - *Cons:* Susceptible to race conditions during concurrent requests without strict serializable isolation or manual table locking.
  - *Decision:* Application checks provide friendly error messages, but the database exclusion constraint is the authoritative guard.

## 3. Currency Isolation vs. Arbitrary Conversion

- **Option A (Chosen): Strict Currency Isolation & Grouping**
  - *Pros:* Accurate, transparent, and legally defensible. Summing $1,000,000 USD with €500,000 EUR directly is meaningless without official foreign exchange conversion rates, rate dates, and hedging policies.
  - *Cons:* Dashboard displays multiple totals (one per currency) rather than a single unified aggregate.
  - *Decision:* Strictly aligned with the prompt's product requirements: do not combine different currencies without documented rates.

- **Option B: Static Arbitrary FX Rates**
  - *Pros:* Single number on dashboard.
  - *Cons:* Gives misleading financial figures and creates hidden currency risks.
  - *Rejected.*

## 4. Server-Side Pagination & In-Database Aggregation vs. Client-Side Processing

- **Option A (Chosen): Server-side Pagination & DB Aggregations (`percentile_cont`, `AVG`, `SUM`)**
  - *Pros:* Easily scales past 10,000 employees without memory bloat or client latency. Client payload is bounded to 15-50 records per request.
  - *Cons:* Requires robust SQL query construction and parameter sanitization.
  - *Decision:* Standard best practice for enterprise data sets.

- **Option B: Client-side Filtering & Pagination**
  - *Pros:* Faster subsequent filtering once loaded.
  - *Cons:* Initial download of 10,000 records (~5-10MB JSON) causes noticeable load delay, mobile browser memory crashes, and security exposure of the full dataset.
  - *Rejected.*

## 5. Session/JWT Authentication: Minimal Role vs. Multi-tenant RBAC

- **Option A (Chosen): Single-Org Token/Session Auth with HR Manager Role**
  - *Pros:* Lean, highly secure, zero unnecessary complexity. Fits the single-organization requirement.
  - *Cons:* Does not provide department-level granular permission hierarchies (e.g., Engineering HR vs. Sales HR).
  - *Decision:* Aligns with the core requirement to avoid premature overengineering while maintaining robust security.
