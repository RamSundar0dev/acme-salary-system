import argparse
import os
import random
import sys
from datetime import date, timedelta
from decimal import Decimal

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from app.db.session import SessionLocal, engine
from app.models.department import Department
from app.models.employee import Employee
from app.models.salary_record import SalaryRecord
from app.models.user import User
from app.scripts.bootstrap_admin import bootstrap_admin

TARGET_EMPLOYEES = 10000

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Margaret", "Anthony", "Betty", "Donald", "Sandra", "Mark", "Ashley",
    "Paul", "Dorothy", "Steven", "Kimberly", "Andrew", "Emily", "Kenneth", "Donna",
    "Joshua", "Michelle", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
    "Edward", "Deborah", "Ronald", "Stephanie", "Timothy", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Shirley", "Eric", "Angela", "Jonathan", "Helen", "Stephen", "Anna",
    "Larry", "Brenda", "Justin", "Pamela", "Scott", "Nicole", "Brandon", "Emma",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Gregory", "Christine", "Frank", "Debra",
    "Alexander", "Rachel", "Raymond", "Catherine", "Patrick", "Carolyn", "Jack", "Janet",
    "Dennis", "Ruth", "Jerry", "Maria", "Tyler", "Heather", "Aaron", "Diane",
    "Jose", "Virginia", "Adam", "Julie", "Henry", "Joyce", "Nathan", "Victoria",
    "Douglas", "Olivia", "Zachary", "Kelly", "Peter", "Christina", "Kyle", "Lauren",
    "Walter", "Joan", "Ethan", "Evelyn", "Jeremy", "Judith", "Harold", "Megan",
    "Keith", "Cheryl", "Christian", "Andrea", "Roger", "Hannah", "Noah", "Martha",
    "Gerald", "Jacqueline", "Carl", "Frances", "Terry", "Ann", "Sean", "Gloria",
    "Austin", "Jean", "Arthur", "Kathryn", "Lawrence", "Alice", "Jesse", "Teresa",
    "Dylan", "Sara", "Bryan", "Janice", "Joe", "Doris", "Jordan", "Madison",
    "Billy", "Julia", "Albert", "Grace", "Bruce", "Judy", "Willie", "Abigail",
    "Gabriel", "Marie", "Logan", "Denise", "Alan", "Beverly", "Juan", "Amber",
    "Wayne", "Theresa", "Roy", "Marilyn", "Ralph", "Danielle", "Randy", "Diana",
    "Eugene", "Brittany", "Vincent", "Natalie", "Russell", "Sophia", "Louis", "Rose",
    "Philip", "Isabella", "Bobby", "Alexis", "Johnny", "Kayla", "Bradley", "Charlotte",
    "Priya", "Arjun", "Rahul", "Ananya", "Rohan", "Sneha", "Vikram", "Pooja",
    "Aarav", "Aditi", "Karan", "Divya", "Siddharth", "Neha", "Amit", "Kavita",
    "Wei", "Hui", "Min", "Lei", "Fang", "Jie", "Ying", "Tatsuya", "Kenji", "Yuki",
    "Lukas", "Leon", "Finn", "Sophie", "Marie", "Mia", "Pierre", "Camille", "Hugo"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
    "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza",
    "Ruiz", "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers",
    "Long", "Ross", "Foster", "Jimenez", "Powell", "Jenkins", "Perry", "Russell",
    "Sullivan", "Bell", "Coleman", "Butler", "Henderson", "Barnes", "Gonzales", "Fisher",
    "Vasquez", "Simmons", "Romero", "Jordan", "Patterson", "Alexander", "Hamilton", "Graham",
    "Reynolds", "Griffin", "Wallace", "Moreno", "West", "Cole", "Hayes", "Bryant",
    "Herrera", "Gibson", "Ellis", "Tran", "Medina", "Aguilar", "Stevens", "Murray",
    "Ford", "Castro", "Marshall", "Owens", "Harrison", "Fernandez", "McDonald", "Woods",
    "Washington", "Kennedy", "Wells", "Vargas", "Henry", "Chen", "Freeman", "Webb",
    "Sharma", "Verma", "Gupta", "Malhotra", "Mehta", "Iyer", "Nair", "Reddy",
    "Tanaka", "Sato", "Suzuki", "Takahashi", "Watanabe", "Muller", "Schmidt", "Schneider"
]

DEPARTMENTS = [
    ("ENG", "Engineering"),
    ("PROD", "Product & Design"),
    ("HR", "Human Resources"),
    ("SALES", "Sales & Business Development"),
    ("MKTG", "Marketing"),
    ("FIN", "Finance & Accounting"),
    ("OPS", "Operations & IT"),
    ("LEGAL", "Legal & Compliance"),
]

COUNTRIES_CONFIG = [
    # (CountryCode, Currency, MinSalary, MaxSalary, Weight)
    ("US", "USD", 65000, 185000, 35),
    ("GB", "GBP", 45000, 125000, 15),
    ("DE", "EUR", 50000, 135000, 15),
    ("CA", "CAD", 60000, 145000, 10),
    ("IN", "INR", 1200000, 4200000, 10),
    ("AU", "AUD", 70000, 155000, 5),
    ("SG", "SGD", 65000, 150000, 5),
    ("JP", "JPY", 6000000, 16000000, 5),
]


def seed_database(reset: bool = False):
    random.seed(42)  # Deterministic generation
    db = SessionLocal()

    try:
        # Check existing count
        existing_count = db.query(Employee).count()
        if existing_count > 0:
            if not reset:
                print(f"Database already contains {existing_count} employees. Use --reset to re-seed.")
                return
            print(f"Resetting existing data ({existing_count} employees)...")
            db.execute(text("DELETE FROM audit_logs;"))
            db.execute(text("DELETE FROM salary_records;"))
            db.execute(text("DELETE FROM employees;"))
            db.execute(text("DELETE FROM departments;"))
            db.commit()

        # 1. Bootstrap Admin
        print("Ensuring admin account exists...")
        bootstrap_admin()
        admin_user = db.query(User).filter(User.role == "hr_manager").first()
        admin_id = admin_user.id if admin_user else None

        # 2. Seed Departments
        print("Seeding departments...")
        dept_ids = []
        for code, name in DEPARTMENTS:
            dept = db.query(Department).filter(Department.code == code).first()
            if not dept:
                dept = Department(code=code, name=name)
                db.add(dept)
                db.flush()
            dept_ids.append(dept.id)
        db.commit()

        # 3. Generate 10,000 Employees
        print(f"Generating exactly {TARGET_EMPLOYEES} synthetic employees...")
        country_choices = []
        for cfg in COUNTRIES_CONFIG:
            country_choices.extend([cfg] * cfg[4])

        base_start_date = date(2018, 1, 1)
        today = date(2026, 10, 1)

        employees_batch = []
        salaries_batch = []

        for i in range(1, TARGET_EMPLOYEES + 1):
            emp_number = f"ACM-{i:06d}"
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            email = f"{fn.lower()}.{ln.lower()}.{i}@acme.corp"
            country_cfg = random.choice(country_choices)
            c_code, curr, min_sal, max_sal, _ = country_cfg
            dept_id = random.choice(dept_ids)

            # Random employment start date between 2018 and 2026
            days_diff = (today - base_start_date).days
            start_date = base_start_date + timedelta(days=random.randint(0, days_diff - 30))

            # Status distribution: 92% ACTIVE, 5% TERMINATED, 3% ON_LEAVE
            status_rand = random.random()
            if status_rand < 0.92:
                emp_status = "ACTIVE"
            elif status_rand < 0.97:
                emp_status = "TERMINATED"
            else:
                emp_status = "ON_LEAVE"

            employees_batch.append({
                "id": i,
                "employee_number": emp_number,
                "first_name": fn,
                "last_name": ln,
                "email": email,
                "country_code": c_code,
                "department_id": dept_id,
                "employment_status": emp_status,
                "employment_start_date": start_date,
            })

            # Initial Salary
            # Round salary nicely
            base_sal = Decimal(str(random.randint(min_sal // 1000, max_sal // 1000) * 1000))

            # Does employee have salary history?
            # 35% of employees have had a merit increase/promotion if hired > 400 days ago
            days_employed = (today - start_date).days
            has_history = (random.random() < 0.35) and (days_employed > 400)

            if has_history:
                # Promotion date after 1-2 years
                promotion_delay = min(days_employed - 60, random.randint(300, 600))
                promo_date = start_date + timedelta(days=promotion_delay)

                # Prior initial salary (closed period)
                salaries_batch.append({
                    "employee_id": i,
                    "amount": base_sal,
                    "currency": curr,
                    "effective_from": start_date,
                    "effective_to": promo_date,
                    "change_reason": "INITIAL_OFFER",
                    "is_correction": False,
                    "correction_notes": None,
                    "created_by": admin_id,
                })

                # Current higher salary
                increase_factor = Decimal(str(random.choice([1.08, 1.12, 1.15, 1.20])))
                new_sal = round(base_sal * increase_factor, 2)
                salaries_batch.append({
                    "employee_id": i,
                    "amount": new_sal,
                    "currency": curr,
                    "effective_from": promo_date,
                    "effective_to": None,
                    "change_reason": random.choice(["MERIT_INCREASE", "PROMOTION", "MARKET_ADJUSTMENT"]),
                    "is_correction": False,
                    "correction_notes": None,
                    "created_by": admin_id,
                })
            else:
                # Single open-ended current salary
                salaries_batch.append({
                    "employee_id": i,
                    "amount": base_sal,
                    "currency": curr,
                    "effective_from": start_date,
                    "effective_to": None,
                    "change_reason": "INITIAL_OFFER",
                    "is_correction": False,
                    "correction_notes": None,
                    "created_by": admin_id,
                })

        # Fast Bulk Insert
        print("Inserting employees batch into PostgreSQL...")
        db.bulk_insert_mappings(Employee, employees_batch)
        db.commit()

        # Update sequence for employees id
        db.execute(text("SELECT setval('employees_id_seq', (SELECT MAX(id) FROM employees));"))
        db.commit()

        print(f"Inserting {len(salaries_batch)} salary records into PostgreSQL...")
        # Insert in chunks of 5000 to optimize PostgreSQL memory
        chunk_size = 5000
        for idx in range(0, len(salaries_batch), chunk_size):
            chunk = salaries_batch[idx : idx + chunk_size]
            db.bulk_insert_mappings(SalaryRecord, chunk)
            db.commit()

        db.execute(text("SELECT setval('salary_records_id_seq', (SELECT MAX(id) FROM salary_records));"))
        db.commit()

        # 4. Verification Check
        emp_count = db.query(Employee).count()
        sal_count = db.query(SalaryRecord).count()
        dept_count = db.query(Department).count()
        active_sal_count = db.query(SalaryRecord).filter(SalaryRecord.effective_to.is_(None)).count()

        print("\n" + "=" * 50)
        print("SEEDING COMPLETED & VERIFIED:")
        print(f"  Total Employees:          {emp_count} (Expected: {TARGET_EMPLOYEES})")
        print(f"  Total Departments:        {dept_count}")
        print(f"  Total Salary Records:     {sal_count}")
        print(f"  Active Current Salaries:  {active_sal_count}")
        print("=" * 50 + "\n")

        assert emp_count == TARGET_EMPLOYEES, f"Expected exactly {TARGET_EMPLOYEES} employees, got {emp_count}"

    except Exception as exc:
        db.rollback()
        print(f"Error during seeding: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deterministic 10,000 employee seed script for ACME Salary System")
    parser.add_argument("--reset", action="store_true", help="Reset existing data before seeding")
    args = parser.parse_args()

    seed_database(reset=args.reset)
