from fastapi import FastAPI
from pathlib import Path
import os
from .routes.api import router as api_router
from .routes.page import router as page_router, init_static_files

app = FastAPI(title="File Browser")

# 从环境变量或默认值获取根目录
ROOT_DIR = Path(os.getenv("FILE_SERVER_ROOT", "./files"))
ROOT_DIR.mkdir(parents=True, exist_ok=True)

# 设置 ROOT_DIR 到 app.state 中，以便在路由中使用
app.state.ROOT_DIR = ROOT_DIR

# 初始化静态文件服务
init_static_files(app)

# 包含路由
app.include_router(api_router)
app.include_router(page_router)