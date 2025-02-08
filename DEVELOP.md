# 开发指南

## 开发环境搭建

1. 克隆仓库：
```bash
git clone https://github.com/codeskyblue/servefs.git
cd servefs
```

2. 安装依赖：
```bash
poetry install
```

3. 运行服务器：
```bash
poetry run servefs
```

也可以使用nodemon来自动重启服务器：(需要提前装node)

```bash
make dev
```

4. 在浏览器中打开：
```
http://localhost:8000
```

## 技术栈

### 后端
- FastAPI: 高性能 Python Web 框架
- Python 3.8+: 编程语言
- uvicorn: ASGI 服务器
- Typer: 命令行界面框架
- Rich: 终端样式美化

### 前端
- Vue.js 3: 前端框架
- Element Plus: UI 组件库
- @element-plus/icons-vue: 图标库

## 开发注意事项

- 文件会自动重命名以避免冲突
- 删除操作需要确认
- 支持的图片格式：jpg、jpeg、png、gif、webp
- 文件大小显示会自动转换单位（B、KB、MB、GB）

## 贡献指南

1. Fork 仓库
2. 创建功能分支
3. 提交更改
4. 提交 Pull Request

## 测试

运行测试：
```bash
pytest
```

## 代码风格

我们使用以下工具来保持代码风格的一致性：

1. black: Python 代码格式化
```bash
poetry run black .
```

2. isort: Python import 语句排序
```bash
poetry run python -m isort .
```
