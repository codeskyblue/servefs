import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from .middleware.auth import AuthManager, AuthMiddleware
from .routes.api import router as api_router
from .routes.page import init_static_files
from .routes.page import router as page_router

# Get debug mode from environment variable
DEBUG = os.getenv("SERVEFS_DEBUG", "false").lower() == "true"

# Configure auth manager
auth_manager = AuthManager()
auth_manager.configure(os.getenv("SERVEFS_BASIC_AUTH"))

# Disable docs and redoc in non-debug mode
app = FastAPI(
    title="File Browser",
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
    openapi_url="/openapi.json" if DEBUG else None,
)

# Get root directory from environment variable or use default
ROOT_DIR = Path(os.getenv("SERVEFS_ROOT", "./files"))
ROOT_DIR.mkdir(parents=True, exist_ok=True)

# Set ROOT_DIR and auth_manager in app.state for use in routes
app.state.ROOT_DIR = ROOT_DIR
app.state.auth_manager = auth_manager

# Add auth middleware
app.add_middleware(AuthMiddleware, auth_manager=auth_manager)

# Add exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    headers = getattr(exc, "headers", None)
    if headers:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=headers,
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Initialize static file serving
init_static_files(app)

# Include routers
app.include_router(api_router)
app.include_router(page_router)