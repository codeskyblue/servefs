from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import mimetypes
import shutil
import os

app = FastAPI(title="File Browser")

# 从环境变量或默认值获取根目录
ROOT_DIR = Path(os.getenv("FILE_SERVER_ROOT", "./files"))
ROOT_DIR.mkdir(parents=True, exist_ok=True)

# 获取当前模块的路径
PACKAGE_DIR = Path(__file__).parent

# API routes
@app.get("/api/files")
async def list_files(path: str = ""):
    """List files and directories at the given path"""
    try:
        target_path = ROOT_DIR / path
        if not target_path.exists():
            return {"error": "Path not found"}
        
        items = []
        for item in target_path.iterdir():
            try:
                is_dir = item.is_dir()
                item_info = {
                    "name": item.name,
                    "path": str(item.relative_to(ROOT_DIR)),
                    "type": "directory" if is_dir else "file",
                    "size": 0 if is_dir else item.stat().st_size,
                    "download_url": f"/download/{item.relative_to(ROOT_DIR)}"
                }
                items.append(item_info)
            except Exception:
                continue

        # 按目录优先、名字升序排序
        items.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
        
        return {
            "items": items,
            "current_path": path
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/download/{file_path:path}")
async def download_file(file_path: str):
    """Download file"""
    try:
        file_path = ROOT_DIR / file_path
        if not file_path.exists() or not file_path.is_file():
            return {"error": "File not found"}
        
        return FileResponse(
            file_path,
            filename=file_path.name,
            media_type="application/octet-stream"
        )
    except Exception as e:
        return {"error": str(e)}

@app.put("/api/files/{file_path:path}")
async def update_file(file_path: str, request: Request):
    """Update file content"""
    try:
        data = await request.json()
        content = data.get("content", "")
        
        file_path = ROOT_DIR / file_path
        if not file_path.exists():
            return {"error": "File not found"}
        
        file_path.write_text(content)
        return {"message": "File updated successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.delete("/api/files/{file_path:path}")
async def delete_file(file_path: str):
    """Delete file or directory"""
    try:
        target_path = ROOT_DIR / file_path
        if not target_path.exists():
            return {"error": "File or directory not found"}
        
        if target_path.is_file():
            target_path.unlink()
        else:
            import shutil
            shutil.rmtree(target_path)
        
        return {"message": "Deleted successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/upload/{path:path}")
async def upload_files(path: str, files: list[UploadFile] = File(...), paths: list[str] = Form(...)):
    """Upload files to the specified path"""
    try:
        target_path = ROOT_DIR / path
        
        uploaded_files = []
        for file, relative_path in zip(files, paths):
            try:
                # 将 Windows 路径分隔符转换为 POSIX 格式
                relative_path = relative_path.replace("\\", "/")
                
                # 构建完整的目标路径
                file_path = target_path / relative_path
                
                # 确保父目录存在
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 如果文件已存在，添加数字后缀
                original_path = file_path
                counter = 1
                while file_path.exists():
                    stem = original_path.stem
                    suffix = original_path.suffix
                    file_path = original_path.parent / f"{stem}_{counter}{suffix}"
                    counter += 1

                # 保存文件
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)
                
                uploaded_files.append({
                    "name": file_path.name,
                    "path": str(file_path.relative_to(ROOT_DIR)),
                    "size": file_path.stat().st_size,
                    "download_url": f"/download/{file_path.relative_to(ROOT_DIR)}"
                })
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to upload {relative_path}: {str(e)}")
        
        return {"files": uploaded_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files for direct access to static assets
app.mount("/static", StaticFiles(directory=PACKAGE_DIR / "static"), name="static")

# Serve index.html for the root path
@app.get("/", response_class=HTMLResponse)
async def serve_root():
    """Serve index.html"""
    return (PACKAGE_DIR / "static/index.html").read_text(encoding="utf-8")

# Redirect /blob/{path} to index.html for client-side routing
@app.get("/blob/{path:path}", response_class=HTMLResponse)
async def serve_blob_path(path: str):
    """Serve index.html for blob paths"""
    return (PACKAGE_DIR / "static/index.html").read_text(encoding="utf-8")

@app.get("/raw/{file_path:path}")
async def get_raw_file(file_path: str):
    """Get raw file content"""
    try:
        file_path = ROOT_DIR / file_path
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="File not found")
        
        # 获取文件的 MIME 类型
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