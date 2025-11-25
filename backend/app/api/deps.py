"""API dependencies for authentication and database access."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.redis import CacheService, get_cache
from app.core.security import decode_token

logger = get_logger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)


class AuthenticatedUser:
    """Represents an authenticated user/API client."""

    def __init__(self, user_id: str, token_type: str = "access"):
        self.user_id = user_id
        self.token_type = token_type

    @property
    def uuid(self) -> UUID | None:
        """Get user ID as UUID if valid."""
        try:
            return UUID(self.user_id)
        except ValueError:
            return None


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(security)
    ],
) -> AuthenticatedUser | None:
    """Get current authenticated user from JWT token.

    Returns None if no valid token is provided.
    """
    if credentials is None:
        return None

    token = credentials.credentials
    token_data = decode_token(token)

    if token_data is None:
        return None

    return AuthenticatedUser(
        user_id=token_data.sub,
        token_type=token_data.type,
    )


async def require_auth(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(security)
    ],
) -> AuthenticatedUser:
    """Require valid authentication.

    Raises HTTPException 401 if not authenticated.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    token_data = decode_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug("Authenticated request", user_id=token_data.sub)

    return AuthenticatedUser(
        user_id=token_data.sub,
        token_type=token_data.type,
    )


# Type aliases for dependency injection
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]
Cache = Annotated[CacheService, Depends(get_cache)]
OptionalAuth = Annotated[AuthenticatedUser | None, Depends(get_current_user)]
RequiredAuth = Annotated[AuthenticatedUser, Depends(require_auth)]
