from fastapi import FastAPI
from pathlib import Path
import os
from .routes.api import router as api_router
from .routes.page import router as page_router, init_static_files

# Get debug mode from environment variable
DEBUG = os.getenv("SERVEFS_DEBUG", "false").lower() == "true"

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

# Set ROOT_DIR in app.state for use in routes
app.state.ROOT_DIR = ROOT_DIR

# Initialize static file serving
init_static_files(app)

# Include routers
app.include_router(api_router)
app.include_router(page_router)