from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
import pyotp
import secrets
import hashlib
import string

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm="HS256"
    )
    return encoded_jwt


def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_REFRESH_SECRET,
        algorithm="HS256"
    )
    return encoded_jwt


def decode_token(token: str, secret: str) -> Optional[dict]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except JWTError:
        return None


def generate_token(length: int = 32) -> str:
    """Generate a secure random token."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def hash_api_key(api_key: str) -> str:
    """Hash an API key for secure storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def generate_totp_secret() -> str:
    """Generate a TOTP secret for 2FA."""
    return pyotp.random_base32()


def verify_totp(secret: str, token: str) -> bool:
    """Verify a TOTP token."""
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)


def create_2fa_token(user_id: str) -> str:
    """Create a short-lived 2FA challenge token."""
    to_encode = {"sub": user_id, "type": "2fa_challenge"}
    expire = datetime.utcnow() + timedelta(minutes=5)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm="HS256"
    )
    return encoded_jwt


def decode_2fa_token(token: str) -> Optional[dict]:
    """Decode and verify a 2FA challenge token."""
    payload = decode_token(token, settings.JWT_SECRET)
    if not payload or payload.get("type") != "2fa_challenge":
        return None
    return payload


def generate_recovery_codes(count: int = 10) -> list[str]:
    """Generate recovery codes for 2FA."""
    codes = []
    for _ in range(count):
        code = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        codes.append(f"{code[:4]}-{code[4:]}")
    return codes


def hash_recovery_code(code: str) -> str:
    """Hash a recovery code for secure storage."""
    return hashlib.sha256(code.replace("-", "").upper().encode()).hexdigest()
