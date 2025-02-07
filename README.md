# Simple HTTP Server

[English](README_EN.md)

一个基于 FastAPI 和 Vue.js 的简单文件服务器，支持文件和文件夹的上传、预览和管理。

## 功能特点

- 📁 文件和文件夹浏览
- 📤 支持文件和文件夹上传
- 🖼️ 图片文件预览
- 🗑️ 文件和文件夹删除
- 📊 文件大小显示
- 🔄 实时进度显示
- 💫 拖放上传支持
- 🖥️ 命令行界面支持

## 安装

推荐使用 `pipx` 安装（保证依赖隔离）：

```bash
pipx install simplehttpserver
```

或者使用 pip 安装：

```bash
pip install simplehttpserver
```

## 使用方法

### 命令行使用

最简单的使用方式：

```bash
# 在当前目录启动服务器
simplehttpserver

# 指定端口号
simplehttpserver --port 7001

# 指定根目录
simplehttpserver --root /path/to/directory

# 查看帮助
simplehttpserver --help
```

完整的命令行选项：

```
选项:
  -r, --root TEXT     要服务的根目录 [default: .]
  -h, --host TEXT     绑定的主机地址 [default: 127.0.0.1]
  -p, --port INTEGER  绑定的端口号 [default: 8000]
  -v, --version       显示版本号并退出
  --help             显示帮助信息并退出
```

### 开发环境使用

1. 克隆仓库：
```bash
git clone [repository-url]
cd fileserver
```

2. 安装依赖：
```bash
poetry install
```

3. 运行服务器：
```bash
poetry run simplehttpserver
```

4. 打开浏览器访问：
```
http://localhost:8000
```

## 技术栈

### 后端
- FastAPI：高性能的 Python Web 框架
- Python 3.8+：编程语言
- uvicorn：ASGI 服务器
- Typer：命令行界面框架
- Rich：终端美化

### 前端
- Vue.js 3：前端框架
- Element Plus：UI 组件库
- @element-plus/icons-vue：图标库

## 注意事项

- 上传文件会自动重命名以避免冲突
- 删除操作需要确认
- 支持的图片格式：jpg、jpeg、png、gif、webp
- 文件大小显示自动转换单位（B、KB、MB、GB）

## 开发计划

- [ ] 添加文件搜索功能
- [ ] 支持更多文件类型的预览
- [ ] 添加文件排序功能
- [ ] 支持文件重命名
- [ ] 添加用户认证
- [ ] 支持文件分享
