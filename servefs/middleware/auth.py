import base64
from typing import Optional, Tuple

from fastapi import Request
from starlette.middleware.base import (BaseHTTPMiddleware,
                                       RequestResponseEndpoint)
from starlette.responses import JSONResponse, Response


class Permission:
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"

class AuthManager:
    """认证管理器，用于存储和管理认证状态"""
    def __init__(self):
        self.auth_enabled = False
        self.username = None
        self.password = None

    def configure(self, basic_auth: Optional[str] = None):
        """配置认证信息"""
        if basic_auth:
            try:
                self.username, self.password = basic_auth.split(':')
                self.auth_enabled = True
            except ValueError:
                raise ValueError("Basic auth must be in format username:password")
        else:
            self.auth_enabled = False

    def check_auth(self, auth_header: Optional[str]) -> Tuple[bool, str]:
        """检查认证信息
        返回: (是否认证成功, 权限级别)
        """
        if not self.auth_enabled:
            return True, Permission.READ_WRITE

        if not auth_header or not auth_header.startswith('Basic '):
            return False, Permission.READ_ONLY

        try:
            auth_data = base64.b64decode(auth_header[6:]).decode('utf-8')
            username, password = auth_data.split(':')
            
            if username == self.username and password == self.password:
                return True, Permission.READ_WRITE
        except Exception:
            pass

        return False, Permission.READ_ONLY

class AuthMiddleware(BaseHTTPMiddleware):
    """FastAPI 认证中间件"""
    def __init__(self, app, auth_manager: AuthManager):
        super().__init__(app)
        self.auth_manager = auth_manager

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """中间件处理函数"""
        # 检查是否是静态文件、前端路由或认证相关请求
        if (request.url.path.startswith("/static") or 
            request.url.path == "/" or 
            request.url.path.startswith("/blob/") or
            request.url.path.startswith("/api/auth/")):
            return await call_next(request)

        # 获取认证头并检查权限
        auth_header = request.headers.get('Authorization')
        is_authenticated, permission = self.auth_manager.check_auth(auth_header)

        # 设置请求状态中的权限
        request.state.permission = permission

        # 对写操作检查权限
        if permission == Permission.READ_ONLY and request.method not in ["GET", "HEAD", "OPTIONS"]:
            if not is_authenticated and self.auth_manager.auth_enabled:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Not authenticated"},
                    headers={"WWW-Authenticate": "Basic"}
                )
            return JSONResponse(
                status_code=403,
                content={"detail": "Read-only access: write operations not permitted"}
            )

        return await call_next(request)
