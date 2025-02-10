import hashlib
import os

from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from starlette.types import Receive, Scope, Send


class ETaggedStaticFiles(StaticFiles):
    """带有 ETag 支持的静态文件处理类"""
    
    async def get_response(self, path: str, scope: Scope) -> FileResponse:
        response = await super().get_response(path, scope)
        if isinstance(response, FileResponse):
            # 获取文件的完整路径
            full_path = os.path.join(self.directory, path)
            
            # 生成 ETag（基于文件大小和最后修改时间）
            stat = os.stat(full_path)
            etag = hashlib.md5(f"{stat.st_size}_{stat.st_mtime}".encode()).hexdigest()
            
            # 设置 ETag 和缓存控制头
            response.headers["ETag"] = f'"{etag}"'
            response.headers["Cache-Control"] = "no-cache"  # 强制重新验证
            
            # 检查客户端的 If-None-Match 头
            if_none_match = None
            for key, value in scope["headers"]:  # headers 是一个 (bytes, bytes) 的列表
                if key == b"if-none-match":
                    if_none_match = value.decode()
                    break
            
            if if_none_match and if_none_match.strip('"') == etag:
                response.status_code = 304  # Not Modified
                response.body = b""
        
        return response
