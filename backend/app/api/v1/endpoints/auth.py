"""Authentication endpoints."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.security import (
    TokenResponse,
    create_access_token,
    hash_password,
    verify_password,
)

router = APIRouter()


class APIKeyRequest(BaseModel):
    """Request to authenticate with API key."""

    api_key: str = Field(description="API key for authentication")


class TokenRefreshRequest(BaseModel):
    """Request to refresh an access token."""

    refresh_token: str = Field(description="Refresh token")


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Get access token",
    description="Exchange API key for a JWT access token",
)
async def get_access_token(request: APIKeyRequest) -> TokenResponse:
    """Authenticate with API key and get access token.

    For development/demo purposes, accepts a predefined API key.
    In production, this would validate against a database of API keys.
    """
    # Demo authentication - in production, validate against stored API keys
    # The demo API key is stored in settings
    demo_api_key = getattr(settings, "demo_api_key", "arbor-demo-key-2024")

    if request.api_key != demo_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    # Create access token
    access_token = create_access_token(
        subject="demo-client",
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post(
    "/token/validate",
    summary="Validate token",
    description="Check if an access token is valid",
)
async def validate_token(
    authorization: str = None,
) -> dict:
    """Validate an access token.

    Returns token details if valid.
    """
    from app.core.security import decode_token

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization header required",
        )

    # Extract token from "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid authorization header format. Use 'Bearer <token>'",
        )

    token = parts[1]
    token_data = decode_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return {
        "valid": True,
        "subject": token_data.sub,
        "expires_at": token_data.exp.isoformat(),
        "token_type": token_data.type,
    }
