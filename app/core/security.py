from app.core.config import settings
from app.domain.dependencies.access_token import get_access_token_db
from fastapi import Depends
from fastapi_users.authentication import BearerTransport, AuthenticationBackend
from fastapi_users.authentication.strategy import AccessTokenDatabase, DatabaseStrategy
from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.models.auth import AccessToken

# Bearer transport used for token-based authentication with the specified login endpoint.
bearer_transport = BearerTransport(tokenUrl="auth/login")


def get_database_strategy(
    access_token_db: AccessTokenDatabase["AccessToken"] = Depends(get_access_token_db),
) -> DatabaseStrategy:
    """
    Returns a database strategy for managing access tokens with a specified lifetime.
    """
    return DatabaseStrategy(
        access_token_db, lifetime_seconds=settings.LIFE_TIME_SECONDS
    )


# Authentication backend configured to use bearer transport and a database strategy.
authentication_backend = AuthenticationBackend(
    name="access-token-db",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)
