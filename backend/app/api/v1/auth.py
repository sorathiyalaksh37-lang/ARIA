"""
Complete Authentication & Authorization API
Registration, Login, Token Management, RBAC
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr, Field

from app.core.database import get_db
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User, UserRole
from app.schemas.response import ResponseBase

router = APIRouter()
security = HTTPBearer()


# ============================================================================
# SCHEMAS
# ============================================================================

class UserRegister(BaseModel):
    """User registration schema."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    organization: Optional[str] = Field(None, max_length=255)
    role: UserRole = UserRole.VIEWER


class UserLogin(BaseModel):
    """User login schema."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response schema."""
    id: UUID
    email: str
    username: str
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class ChangePassword(BaseModel):
    """Change password schema."""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


# ============================================================================
# REGISTER
# ============================================================================

@router.post(
    "/register",
    response_model=ResponseBase,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account"
)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    
    - **email**: Unique email address
    - **username**: Unique username (3-50 chars)
    - **password**: Strong password (min 8 chars)
    - **full_name**: Full name
    - **role**: User role (default: VIEWER)
    """
    # Check if username exists
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        phone=user_data.phone,
        organization=user_data.organization,
        is_active=True,
        is_verified=False,  # Require email verification in production
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return ResponseBase(
        success=True,
        message="User registered successfully",
        data={
            "user_id": str(user.id),
            "username": user.username,
            "email": user.email
        }
    )


# ============================================================================
# LOGIN
# ============================================================================

@router.post(
    "/login",
    response_model=ResponseBase,
    summary="User login",
    description="Authenticate and get access tokens"
)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with username and password.
    
    Returns access token and refresh token.
    """
    # Find user
    result = await db.execute(
        select(User).where(User.username == credentials.username)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Check if active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create tokens
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active,
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return ResponseBase(
        success=True,
        message="Login successful",
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60,  # 30 minutes
        )
    )


# ============================================================================
# REFRESH TOKEN
# ============================================================================

@router.post(
    "/refresh",
    response_model=ResponseBase,
    summary="Refresh access token",
    description="Get new access token using refresh token"
)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token."""
    token = credentials.credentials
    
    # Decode refresh token
    try:
        payload = decode_token(token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Verify token type
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    # Get user
    user_id = UUID(payload.get("sub"))
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active,
    }
    
    access_token = create_access_token(token_data)
    
    return ResponseBase(
        success=True,
        message="Token refreshed successfully",
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 30 * 60
        }
    )


# ============================================================================
# GET CURRENT USER
# ============================================================================

@router.get(
    "/me",
    response_model=ResponseBase,
    summary="Get current user",
    description="Get current authenticated user information"
)
async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get current user information."""
    from app.core.security import decode_token
    
    token = credentials.credentials
    payload = decode_token(token)
    
    # Get user from database
    user_id = UUID(payload.get("sub"))
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return ResponseBase(
        success=True,
        message="User retrieved successfully",
        data=UserResponse.from_orm(user)
    )


# ============================================================================
# CHANGE PASSWORD
# ============================================================================

@router.put(
    "/password",
    response_model=ResponseBase,
    summary="Change password",
    description="Change user password"
)
async def change_password(
    password_data: ChangePassword,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Change user password."""
    from app.core.security import decode_token
    
    token = credentials.credentials
    payload = decode_token(token)
    
    # Get user
    user_id = UUID(payload.get("sub"))
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify old password
    if not verify_password(password_data.old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid old password"
        )
    
    # Update password
    user.hashed_password = get_password_hash(password_data.new_password)
    await db.commit()
    
    return ResponseBase(
        success=True,
        message="Password changed successfully",
        data=None
    )


# ============================================================================
# LOGOUT
# ============================================================================

@router.post(
    "/logout",
    response_model=ResponseBase,
    summary="Logout",
    description="Logout user (client should discard tokens)"
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Logout user.
    Note: With JWT, actual logout is handled client-side by discarding tokens.
    In production, implement token blacklist in Redis.
    """
    return ResponseBase(
        success=True,
        message="Logged out successfully",
        data=None
    )
