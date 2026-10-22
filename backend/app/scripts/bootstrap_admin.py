import argparse
import sys
import os

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.session import SessionLocal
from app.core.config import settings
from app.services.auth_service import AuthService


def bootstrap_admin(email: str = None, password: str = None, name: str = None):
    admin_email = email or settings.ADMIN_EMAIL
    admin_password = password or settings.ADMIN_INITIAL_PASSWORD
    admin_name = name or settings.ADMIN_NAME

    db = SessionLocal()
    try:
        user = AuthService.ensure_admin_exists(
            db=db,
            email=admin_email,
            password=admin_password,
            full_name=admin_name,
        )
        print(f"Successfully bootstrapped HR Manager account: {user.email} (ID: {user.id})")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bootstrap initial ACME HR Manager administrator account")
    parser.add_argument("--email", type=str, default=None, help="Administrator email")
    parser.add_argument("--password", type=str, default=None, help="Administrator password")
    parser.add_argument("--name", type=str, default=None, help="Administrator full name")
    args = parser.parse_args()

    bootstrap_admin(email=args.email, password=args.password, name=args.name)
