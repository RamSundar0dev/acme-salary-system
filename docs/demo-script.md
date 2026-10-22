# ACME Salary Management System - 5-Minute Evaluation Demo Walkthrough

## 1. Overview
This script guides an evaluator through the primary workflows of the ACME Employee Salary Management System. The application manages compensation for 10,000 employees with strict PostgreSQL data integrity, effective dating, and audit trails.

## 2. Walkthrough Steps

### Step 1: Authentication & Role Gate (0:00 - 0:45)
1. Navigate to `http://localhost:3000/login`.
2. Notice the clean, modern enterprise design and security badge.
3. Observe the pre-filled demo credentials:
   - **Email:** `hr.manager@acme.corp`
   - **Password:** `AcmeHR2026!SecurePass`
4. Click **Sign In to HR Portal**.
5. *Verification:* The user is authenticated via JWT, an HTTP-only cookie is stored, and the client redirects to the HR Executive Dashboard.

### Step 2: HR Analytics Dashboard & Currency Isolation (0:45 - 1:45)
1. On the dashboard (`/`), observe:
   - **Total Workforce:** 10,000 employees.
   - **Active Staff:** ~9,200 employees.
   - **Inactive / On Leave:** ~800 employees.
2. Examine the **Active Payroll Totals by Currency** card:
   - Observe that USD, EUR, GBP, CAD, INR, AUD, SGD, and JPY are strictly separated.
   - Zero misleading currency blending occurs without verified exchange rates.
3. Interact with the **Analytics Filters** bar:
   - Filter by Country: `United States (US)`.
   - Observe that the metrics update dynamically in real time (< 50ms) via in-database SQL aggregation.
4. Toggle the **Compensation Analytics** chart:
   - View the **Distribution** histogram (salary brackets).
   - Switch to **By Department** view to compare Average vs. Median salaries computed using PostgreSQL native `percentile_cont(0.5)`.

### Step 3: 10,000 Employee Directory (1:45 - 2:45)
1. Navigate to **Employee Directory** (`/employees`) in the sidebar.
2. Observe server-side pagination:
   - `Showing 1 to 15 of 10,000 employees`.
3. Test Server-side Search:
   - In the search bar, type `ACM-000042` or `Priya` or `Smith`.
   - Observe immediate indexed search results without loading 10,000 rows into the browser.
4. Test Faceted Filtering:
   - Select Department: `Engineering`.
   - Select Status: `Active`.
5. Test Sorting:
   - Click column headers (Employee ID, Name, Country, Status) to verify server-side sorting.
6. Click **Profile** on any employee (e.g., `ACM-000001`).

### Step 4: Employee Profile & Compensation History (2:45 - 3:45)
1. On `/employees/1`, inspect the employee overview:
   - Employee Number, Work Email, Department, Country, Hire Date, Status.
   - **Active Effective Salary** card highlighting current compensation and ISO 4217 currency.
2. Scroll to the **Compensation History & Audit** timeline:
   - Observe the chronological progression.
   - Notice that each period has an inclusive start date and exclusive end date (or "Open-ended (Present)").

### Step 5: Recording a Salary Change & Validation (3:45 - 4:45)
1. Click **Record Salary Change** (or **Propose Salary Change**).
2. Test Validation:
   - Enter a negative value (`-5000`) or invalid date.
   - Notice instant client validation feedback preventing submission.
3. Enter valid new compensation:
   - **Amount:** `125000`
   - **Effective From:** Select a future date or today.
   - **Reason:** `Promotion / Level Advancement`.
4. Click **Review Proposed Change**:
   - Review the two-step confirmation dialog showing the exact proposed increase, delta, and percentage.
5. Click **Confirm & Save Salary**:
   - The transaction commits atomically in PostgreSQL.
   - The previous active salary record has its `effective_to` automatically capped.
   - The new salary becomes the active compensation.
   - An immutable record is created in `audit_logs`.
6. Inspect the refreshed timeline showing the new record with the "Current Active" badge.

### Step 6: CSV Export & Return to Dashboard (4:45 - 5:00)
1. Click **Export Employees CSV** in the sidebar.
2. A filtered CSV file (`acme_employees_YYYYMMDD_HHMMSS.csv`) downloads instantly via memory-conscious server-side streaming.
3. Return to the **Dashboard** (`/`).
4. Inspect the **Recent Compensation Changes** table:
   - Observe your newly recorded salary increase displayed with the exact timestamp, change reason, and "HR Operations Manager" actor attribution.
