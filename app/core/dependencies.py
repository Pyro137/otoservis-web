from typing import Optional
from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.core.enums import UserRole
from app.services.auth_service import AuthService


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Get the current authenticated user from the session."""
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=303, headers={"Location": "/auth/login"})

    service = AuthService(db)
    user = service.get_user_by_id(user_id)
    if not user or not user.is_active:
        request.session.clear()
        raise HTTPException(status_code=303, headers={"Location": "/auth/login"})
    return user


def get_optional_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Get the current user if authenticated, otherwise None."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    service = AuthService(db)
    return service.get_user_by_id(user_id)


def require_admin(request: Request, db: Session = Depends(get_db)) -> User:
    """Require admin role."""
    user = get_current_user(request, db)
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Bu işlem için yetkiniz yok.")
    return user
