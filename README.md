# ServeFS

[English](README_EN.md)

一个基于 FastAPI 和 Vue.js 的简单文件服务器，支持文件和文件夹的上传、预览和管理。

![screenshot](docs/servefs.png)

更多截图查看 [GALLERY](GALERY.md)

## 功能特点

- 📁 文件和文件夹浏览
- 📤 支持文件和文件夹上传
- 🖼️ 图片文件预览
- 🗑️ 文件和文件夹删除
- 📊 文件大小显示
- 🔄 实时进度显示
- 💫 拖放上传支持
- 🖥️ 命令行界面支持

## 预览功能

- .jpg、.jpeg、.png、.gif、.webp 图片预览。
- .json、.html、.css、.txt、.md、.py 以文本格式预览。
- .ttf 字体文件预览。

## 安装

推荐使用 `pipx` 安装（保证依赖隔离）：

```bash
pipx install servefs
```

或使用 pip：

```bash
pip install servefs
```

## 使用

### 命令行

基本用法：

```bash
# 在当前目录启动服务器
servefs

# 指定端口
servefs --port 7001

# 指定根目录
servefs --root /path/to/directory

# 显示帮助
servefs --help
```

完整命令行选项：

```
选项:
  -r, --root TEXT     要服务的根目录 [default: .]
  -h, --host TEXT     绑定的主机地址 [default: 0.0.0.0]
  -p, --port INTEGER  绑定的端口号 [default: 8000]
  -v, --version       显示版本号并退出
  --help             显示帮助信息并退出
```

## 开发

如果你想参与开发，请查看 [开发指南](DEVELOP.md)。

## TODO

- [ ] 支持文件搜索
- [x] 支持文件重命名
- [ ] 添加用户认证
- [ ] 支持文件分享

## 感谢

- Windsurf