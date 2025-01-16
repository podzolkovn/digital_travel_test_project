from fastapi import APIRouter, Depends
from .auth import router as auth_router
from .order import router as order_router

from fastapi.security import HTTPBearer

# Configure HTTPBearer security for endpoints
http_bearer: HTTPBearer = HTTPBearer(auto_error=False)

# Main API router
router: APIRouter = APIRouter(
    dependencies=[
        Depends(http_bearer),
    ],
)

# Include authentication and order routers
router.include_router(auth_router)
router.include_router(order_router)
