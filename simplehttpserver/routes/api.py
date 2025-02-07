from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
import shutil
from pathlib import Path
import mimetypes

router = APIRouter(prefix="/api", tags=["api"])

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

        # 按目录优先、名字升序排序
        items.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
        
        return {
            "items": items,
            "current_path": path
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/files/{file_path:path}")
async def get_file_content(file_path: str, request: Request):
    """获取文件内容"""
    try:
        file_path = request.app.state.ROOT_DIR / file_path
        if not file_path.exists() or not file_path.is_file():
            return {"error": "文件不存在"}
        
        # 获取文件的 MIME 类型
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type is None:
            mime_type = "application/octet-stream"
        
        # 只读取文本文件
        if not mime_type.startswith('text/'):
            return {"error": "不支持的文件类型"}
            
        try:
            content = file_path.read_text(encoding='utf-8')
            return {"content": content}
        except UnicodeDecodeError:
            return {"error": "不支持的文件编码"}
        
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

@router.post("/upload/{path:path}")
async def upload_files(path: str, files: list[UploadFile] = File(...), paths: list[str] = Form(...), request: Request = None):
    """Upload files to the specified path"""
    try:
        target_path = request.app.state.ROOT_DIR / path
        
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
                    "path": str(file_path.relative_to(request.app.state.ROOT_DIR)),
                    "size": file_path.stat().st_size,
                    "download_url": f"/download/{file_path.relative_to(request.app.state.ROOT_DIR)}"
                })
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to upload {relative_path}: {str(e)}")
        
        return {"files": uploaded_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
