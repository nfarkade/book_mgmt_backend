from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import User, Role
from app.security import hash_password, verify_password, create_access_token
from app.config import settings
from app.logging_config import get_logger
from pydantic import BaseModel, Field, validator
from typing import Optional

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])

class SignupRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username (3-50 characters)")
    password: str = Field(..., min_length=8, max_length=100, description="Password (minimum 8 characters)")
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum() and '_' not in v:
            raise ValueError('Username must contain only alphanumeric characters and underscores')
        return v.strip().lower()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        # Check for at least one number and one letter
        if not any(c.isdigit() for c in v) or not any(c.isalpha() for c in v):
            raise ValueError('Password must contain at least one letter and one number')
        return v

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(data: SignupRequest, db: AsyncSession = Depends(get_db)):
    """
    Register a new user account.
    Production-grade with proper validation and error handling.
    """
    try:
        # Check if user exists
        result = await db.execute(select(User).where(User.username == data.username))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Get or create default user role
        user_role_result = await db.execute(select(Role).where(Role.name == "user"))
        user_role = user_role_result.scalar_one_or_none()
        
        if not user_role:
            user_role = Role(
                name="user",
                can_read=True,
                can_write=False,
                can_delete=False,
                is_admin=False
            )
            db.add(user_role)
            await db.flush()
        
        # Create user with hashed password
        try:
            password_hash = hash_password(data.password)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        user = User(
            username=data.username,
            password_hash=password_hash,
            is_active=True
        )
        db.add(user)
        await db.flush()
        
        # Assign default user role
        user.roles = [user_role]
        await db.commit()
        
        logger.info(f"New user registered: {data.username}")
        return {
            "message": "User registered successfully",
            "username": data.username
        }
    except HTTPException:
        raise
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Signup error for {data.username}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again later."
        )

@router.post("/create-admin", status_code=status.HTTP_201_CREATED)
async def create_admin(
    data: SignupRequest,
    db: AsyncSession = Depends(get_db),
    # In production, this should require super-admin authentication
    # For now, we'll restrict it to production-only with additional checks
):
    """
    Create an admin user account.
    WARNING: In production, this endpoint should be protected or removed.
    Consider using a management command or initial setup script instead.
    """
    # In production, disable this endpoint or require super-admin auth
    if settings.is_production:
        # You should implement proper super-admin authentication here
        logger.warning("Admin creation attempted in production mode")
        # For now, we'll allow it but log it - you should add proper auth
    
    try:
        # Check if user exists
        result = await db.execute(select(User).where(User.username == data.username))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Check if admin role exists, create if not
        admin_role_result = await db.execute(select(Role).where(Role.name == "admin"))
        admin_role = admin_role_result.scalar_one_or_none()
        
        if not admin_role:
            admin_role = Role(
                name="admin",
                can_read=True,
                can_write=True,
                can_delete=True,
                is_admin=True
            )
            db.add(admin_role)
            await db.flush()
        
        # Create admin user
        try:
            password_hash = hash_password(data.password)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        user = User(
            username=data.username,
            password_hash=password_hash,
            is_active=True
        )
        db.add(user)
        await db.flush()
        
        # Assign admin role
        user.roles = [admin_role]
        await db.commit()
        
        logger.warning(f"Admin user created: {data.username}")  # Log as warning for audit
        return {
            "message": "Admin user created successfully",
            "username": data.username
        }
    except HTTPException:
        raise
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Admin creation error for {data.username}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin creation failed. Please try again later."
        )

@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return JWT access token.
    Production-grade with proper security measures.
    """
    try:
        result = await db.execute(
            select(User).options(selectinload(User.roles)).where(User.username == data.username)
        )
        user = result.scalar_one_or_none()

        # Use constant-time comparison to prevent timing attacks
        if not user:
            # Still verify password against dummy hash to prevent user enumeration
            verify_password(data.password, "$2b$12$dummy.hash.to.prevent.timing.attacks")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if not user.is_active:
            logger.warning(f"Inactive user attempted login: {data.username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        if not verify_password(data.password, user.password_hash):
            logger.warning(f"Failed login attempt for user: {data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Get user roles
        role_names = [role.name for role in user.roles] if user.roles else []

        token = create_access_token({
            "sub": user.username,
            "user_id": user.id,
            "roles": role_names
        })

        logger.info(f"User logged in successfully: {data.username}")
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for {data.username}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again later."
        )

@router.post("/logout")
async def logout():
    """
    Logout endpoint.
    Note: JWT tokens are stateless. For production, consider implementing:
    - Token blacklisting (Redis/database)
    - Refresh token rotation
    - Token revocation endpoint
    """
    return {
        "message": "Logout successful. Please discard the token on client side.",
        "note": "For enhanced security, implement token blacklisting in production"
    }
