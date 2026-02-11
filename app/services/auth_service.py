from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import hash_password, verify_password
from app.core.enums import UserRole
from app.repositories.user_repo import UserRepository


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self.repo.get_by_username(username)
        if not user or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create_user(
        self,
        username: str,
        password: str,
        full_name: str,
        role: UserRole = UserRole.TECHNICIAN,
    ) -> User:
        hashed = hash_password(password)
        return self.repo.create(
            {
                "username": username,
                "hashed_password": hashed,
                "full_name": full_name,
                "role": role,
            }
        )

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.repo.get_by_id(user_id)

    def get_all_users(self):
        return self.repo.get_all()

    def get_technicians(self):
        from sqlalchemy import and_
        return self.repo.db.query(User).filter(
            User.is_active == True  # noqa: E712
        ).all()
