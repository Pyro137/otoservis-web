import bcrypt
import secrets
from itsdangerous import URLSafeTimedSerializer
from app.core.config import settings


_serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def generate_csrf_token(session_id: str) -> str:
    """Generate a CSRF token tied to a session."""
    return _serializer.dumps(session_id, salt="csrf-token")


def validate_csrf_token(token: str, session_id: str, max_age: int = 3600) -> bool:
    """Validate a CSRF token."""
    try:
        data = _serializer.loads(token, salt="csrf-token", max_age=max_age)
        return data == session_id
    except Exception:
        return False


def generate_session_id() -> str:
    """Generate a cryptographically secure session ID."""
    return secrets.token_hex(32)
