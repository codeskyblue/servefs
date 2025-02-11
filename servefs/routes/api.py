import mimetypes
import shutil
from typing import List

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from ..middleware.auth import Permission

router = APIRouter(prefix="/api", tags=["api"])

@router.get("/auth/login")
async def login(request: Request):
    """触发浏览器的基本认证对话框"""
    auth_header = request.headers.get("authorization")
    auth_manager = request.app.state.auth_manager
    
    if not auth_manager.auth_enabled:
        return {"message": "Authentication not enabled"}
    
    is_auth, permission = auth_manager.check_auth(auth_header)
    if not is_auth or permission != Permission.READ_WRITE:
        return JSONResponse(
            status_code=401,
            content={"detail": "Authentication required"},
            headers={"WWW-Authenticate": "Basic"}
        )
    
    return {"message": "Authenticated successfully"}

@router.get("/auth/check")
async def check_auth(request: Request):
    """检查当前用户的权限状态"""
    auth_header = request.headers.get("authorization")
    auth_manager = request.app.state.auth_manager
    
    _, permission = auth_manager.check_auth(auth_header)
    return {
        "permission": permission,
        "can_write": permission == Permission.READ_WRITE
    }

@router.get("/files")
async def list_files(path: str = "", request: Request = None):
    """List files and directories at the given path"""
    try:
        target_path = request.app.state.ROOT_DIR / path
        if not target_path.exists():
            return {"error": "Path not found"}
        
        items = []
        for item in target_path.iterdir():
            try:
                is_dir = item.is_dir()
                mime_type = None
                if not is_dir:
                    mime_type, _ = mimetypes.guess_type(str(item))
                    if mime_type is None:
                        mime_type = "application/octet-stream"
                
                item_info = {
                    "name": item.name,
                    "path": str(item.relative_to(request.app.state.ROOT_DIR)),
                    "type": "directory" if is_dir else "file",
                    "size": 0 if is_dir else item.stat().st_size,
                    "download_url": f"/download/{item.relative_to(request.app.state.ROOT_DIR)}",
                    "mime_type": mime_type if not is_dir else None
                }
                items.append(item_info)
            except Exception:
                continue

        # Sort by directory first, then by name ascending
        items.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
        
        return {
            "items": items,
            "current_path": path
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/files/{file_path:path}")
async def get_file_content(file_path: str, request: Request):
    """Get file content"""
    try:
        file_path = request.app.state.ROOT_DIR / file_path
        if not file_path.exists() or not file_path.is_file():
            return {"error": "File not found"}
        
        # Get file MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type is None:
            mime_type = "application/octet-stream"
        
        # Read text files and JSON files
        if not (mime_type.startswith('text/') or mime_type == 'application/json'):
            return {"error": "Unsupported file type"}
            
        try:
            content = file_path.read_text(encoding='utf-8')
            return {"content": content}
        except UnicodeDecodeError:
            return {"error": "Unsupported file encoding"}
        
    except Exception as e:
        return {"error": str(e)}

@router.put("/files/{file_path:path}")
async def update_file(file_path: str, request: Request):
    """Update file content"""
    try:
        data = await request.json()
        content = data.get("content", "")
        
        file_path = request.app.state.ROOT_DIR / file_path
        if not file_path.exists():
            return {"error": "File not found"}
        
        file_path.write_text(content)
        return {"message": "File updated successfully"}
    except Exception as e:
        return {"error": str(e)}

@router.delete("/files/{file_path:path}")
async def delete_file(file_path: str, request: Request):
    """Delete file or directory"""
    try:
        target_path = request.app.state.ROOT_DIR / file_path
        if not target_path.exists():
            return {"error": "File or directory not found"}
        
        if target_path.is_file():
            target_path.unlink()
        else:
            shutil.rmtree(target_path)
        
        return {"message": "Deleted successfully"}
    except Exception as e:
        return {"error": str(e)}

@router.post("/files/{file_path:path}/rename")
async def rename_file(file_path: str, request: Request):
    """重命名文件或目录"""
    try:
        data = await request.json()
        new_name = data.get("new_name", "")
        
        if not new_name:
            return {"error": "新文件名不能为空"}
            
        source_path = request.app.state.ROOT_DIR / file_path
        if not source_path.exists():
            return {"error": "文件或目录不存在"}
            
        # 构建新路径
        target_path = source_path.parent / new_name
        
        # 检查目标文件是否已存在
        if target_path.exists():
            return {"error": "目标文件已存在"}
            
        try:
            source_path.rename(target_path)
            return {
                "message": "重命名成功",
                "new_path": str(target_path.relative_to(request.app.state.ROOT_DIR))
            }
        except OSError as e:
            return {"error": f"重命名失败: {str(e)}"}
            
    except Exception as e:
        return {"error": str(e)}

@router.post("/upload/{path:path}")
async def upload_files(path: str, files: List[UploadFile] = File(...), paths: List[str] = Form(...), request: Request = None):
    """Upload files to the specified path"""
    try:
        target_path = request.app.state.ROOT_DIR / path
        
        uploaded_files = []
        for file, relative_path in zip(files, paths):
            try:
                # Convert Windows path separators to POSIX format
                relative_path = relative_path.replace("\\", "/")
                
                # Build complete target path
                file_path = target_path / relative_path
                
                # Ensure parent directory exists
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # If file exists, add numeric suffix
                original_path = file_path
                counter = 1
                while file_path.exists():
                    stem = original_path.stem
                    suffix = original_path.suffix
                    file_path = original_path.parent / f"{stem}_{counter}{suffix}"
                    counter += 1

                # Save file
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)
                
                uploaded_files.append({
                    "name": file_path.name,
                    "path": str(file_path.relative_to(request.app.state.ROOT_DIR)),
                    "size": file_path.stat().st_size,
                    "download_url": f"/download/{file_path.relative_to(request.app.state.ROOT_DIR)}"
                })
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to upload {relative_path}: {str(e)}")
        
        return {"files": uploaded_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
