from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    user = AuthService.authenticate_user(db, login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token_resp = AuthService.create_user_token(user)

    # Set secure HTTP-only cookie
    response.set_cookie(
        key="auth_token",
        value=token_resp.access_token,
        httponly=True,
        max_age=8 * 3600,
        samesite="lax",
        secure=False,  # Set to True in production HTTPS
    )

    return token_resp


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="auth_token")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user
