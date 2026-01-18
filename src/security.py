from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.config import settings
from typing import Optional, Dict, Any
import secrets

# Production-grade password hashing using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Use settings for secret key and algorithm
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    """
    Hash password using bcrypt for production security.
    Never use SHA256 or MD5 for password hashing.
    """
    if not password or len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash using bcrypt.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token with proper expiration.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    # Use secret key from settings, ensure it's set
    secret_key = settings.SECRET_KEY
    if not secret_key or secret_key == "super-secret-key-change-in-production":
        raise ValueError("SECRET_KEY must be set to a secure random value in production")
    
    return jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify JWT token.
    Returns None if token is invalid.
    """
    try:
        secret_key = settings.SECRET_KEY
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.
    """
    return secrets.token_urlsafe(length)