import mimetypes
import os
from pathlib import Path
from typing import AsyncIterator, Union

import aiofiles
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

# Get current module path
PACKAGE_DIR = Path(__file__).parent.parent

router = APIRouter(tags=["page"])

async def stream_file_range(file_path: Path, start: int, end: int) -> AsyncIterator[bytes]:
    """以块的方式流式读取文件"""
    chunk_size = 4 * 1024 * 1024  # 4MB 块大小，提高传输速度
    async with aiofiles.open(file_path, mode="rb") as f:
        await f.seek(start)
        bytes_remaining = end - start + 1
        while bytes_remaining > 0:
            chunk = await f.read(min(chunk_size, bytes_remaining))
            if not chunk:
                break
            bytes_remaining -= len(chunk)
            yield chunk

async def handle_file_request(
    file_path: Path,
    range_header: str = None,
    as_attachment: bool = False
) -> Union[FileResponse, StreamingResponse]:
    """处理文件请求的通用函数"""
    try:
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="File not found")
            
        file_size = os.path.getsize(file_path)
        mime_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        
        # 如果是下载请求，强制使用 application/octet-stream
        if as_attachment:
            mime_type = "application/octet-stream"
            
        # 如果没有 Range 头，直接返回完整文件
        if not range_header:
            headers = {}
            if as_attachment:
                headers["Content-Disposition"] = f'attachment; filename="{file_path.name}"'
            else:
                headers["Content-Disposition"] = f'inline; filename="{file_path.name}"'
                
            return FileResponse(
                path=file_path,
                media_type=mime_type,
                headers=headers
            )
            
        try:
            # 解析 Range 头
            start, end = range_header.replace("bytes=", "").split("-")
            start = int(start) if start else 0
            end = min(int(end), file_size - 1) if end else file_size - 1
            
            if start >= file_size:
                raise HTTPException(status_code=416, detail="Range not satisfiable")
                
            headers = {
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(end - start + 1),
                "Content-Type": mime_type,
                "Content-Disposition": "attachment" if as_attachment else "inline" + f'; filename="{file_path.name}"'
            }
            
            return StreamingResponse(
                stream_file_range(file_path, start, end),
                status_code=206,
                headers=headers
            )
            
        except (ValueError, IndexError):
            raise HTTPException(status_code=416, detail="Invalid range header")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    """Get raw file content with Range support"""
    try:
        file_path = request.app.state.ROOT_DIR / file_path
        return await handle_file_request(
            file_path=file_path,
            range_header=request.headers.get("range"),
            as_attachment=False
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{file_path:path}")
async def download_file(file_path: str, request: Request):
    """Download file with Range support"""
    try:
        file_path = request.app.state.ROOT_DIR / file_path
        return await handle_file_request(
            file_path=file_path,
            range_header=request.headers.get("range"),
            as_attachment=True
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
