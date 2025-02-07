from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import mimetypes

# Get current module path
PACKAGE_DIR = Path(__file__).parent.parent

router = APIRouter(tags=["page"])

# Mount static files for direct access to static assets
def init_static_files(app):
    """Initialize static file serving"""
    app.mount("/static", StaticFiles(directory=PACKAGE_DIR / "static"), name="static")

# Serve index.html for the root path
@router.get("/", response_class=HTMLResponse)
async def serve_root():
    """Serve index.html"""
    return (PACKAGE_DIR / "static/index.html").read_text(encoding="utf-8")

# Redirect /blob/{path} to index.html for client-side routing
@router.get("/blob/{path:path}", response_class=HTMLResponse)
async def serve_blob_path(path: str):
    """Serve index.html for blob paths"""
    return (PACKAGE_DIR / "static/index.html").read_text(encoding="utf-8")

@router.get("/raw/{file_path:path}")
async def get_raw_file(file_path: str, request: Request):
    """Get raw file content"""
    try:
        file_path = request.app.state.ROOT_DIR / file_path
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get file MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type is None:
            mime_type = "application/octet-stream"
            
        return FileResponse(
            path=file_path,
            media_type=mime_type,
            filename=file_path.name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{file_path:path}")
async def download_file(file_path: str, request: Request):
    """Download file"""
    try:
        file_path = request.app.state.ROOT_DIR / file_path
        if not file_path.exists() or not file_path.is_file():
            return {"error": "File not found"}
        
        return FileResponse(
            file_path,
            filename=file_path.name,
            media_type="application/octet-stream"
        )
    except Exception as e:
        return {"error": str(e)}
