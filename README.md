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

```bash
# 在当前目录启动服务器
servefs

# 指定目录
servefs --directory /path/to/directory
# or
servefs -d /path/to/directory

# 指定端口
servefs --port 7001
# or
servefs -p 7001

# 显示帮助
servefs --help
```

完整命令行选项：

```
选项:
  -d, --directory TEXT     要服务的根目录 [default: .]
  -h, --host TEXT     绑定的主机地址 [default: 0.0.0.0]
  -p, --port INTEGER  绑定的端口号 [default: 8000]
  -b, --basic-auth TEXT  启用基本认证，格式为 username:password
  -v, --version       显示版本号并退出
  --help             显示帮助信息并退出
```

### 基本认证

你可以使用基本认证来限制文件的访问权限：

```bash
# 设置用户名和密码
servefs --basic-auth admin:password123

# 或使用短选项
servefs -b admin:password123
```

启用基本认证后：
- 未认证用户只能查看和下载文件
- 认证用户可以执行所有操作（上传、删除、重命名等）
- 认证信息会通过浏览器的基本认证机制传输

你也可以通过环境变量设置认证信息：

```bash
export SERVEFS_BASIC_AUTH=admin:password123
servefs
```

## 开发

如果你想参与开发，请查看 [开发指南](DEVELOP.md)。

## TODO

- [x] 支持文件重命名
- [x] 支持链接复制
- [x] 添加用户认证
- [ ] 支持文件搜索
- [ ] 支持文件分享

## 相关项目
- https://github.com/Densaugeo/uploadserver 如果只是要上传，下载这个应该就够了
- https://github.com/codeskyblue/gohttpserver 我以前用Golang写的一个版本，现在的项目也是参考的这个
- https://github.com/sigoden/dufs Rust实现的文件服务器，支持文件预览，编辑
- https://github.com/TheWaWaR/simple-http-server 也是Rust写的，比上面那个简单些
- https://min.io 重量级项目，golang实现

## 感谢

- Windsurf