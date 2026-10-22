from typing import Optional
from sqlalchemy.orm import Session
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse


class AuthService:
    @staticmethod
    def authenticate_user(db: Session, login_data: LoginRequest) -> Optional[User]:
        user = db.query(User).filter(User.email == login_data.email.lower()).first()
        if not user or not user.is_active:
            return None
        if not verify_password(login_data.password, user.password_hash):
            return None
        return user

    @staticmethod
    def create_user_token(user: User) -> TokenResponse:
        token = create_access_token(subject=str(user.id))
        return TokenResponse(access_token=token)

    @staticmethod
    def ensure_admin_exists(
        db: Session, email: str, password: str, full_name: str
    ) -> User:
        user = db.query(User).filter(User.email == email.lower()).first()
        if not user:
            user = User(
                email=email.lower(),
                password_hash=get_password_hash(password),
                full_name=full_name,
                role="hr_manager",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
