# Web File Server

A simple file server based on FastAPI and Vue.js, supporting file/folder upload, preview, and management.

## Features

- 📁 File and folder browsing
- 📤 File and folder upload support
- 🖼️ Image file preview
- 🗑️ File and folder deletion
- 📊 File size display
- 🔄 Real-time progress display
- 💫 Drag and drop support
- 🖥️ Command-line interface

## Installation

Recommended installation using `pipx` (for dependency isolation):

```bash
pipx install servefs
```

Or using pip:

```bash
pip install servefs
```

## Usage

### Command Line Usage

Basic usage:

```bash
# Start server in current directory
servefs

# Specify port
servefs --port 7001

# Specify root directory
servefs --root /path/to/directory

# Show help
servefs --help
```

Complete command line options:

```
Options:
  -r, --root TEXT     Root directory to serve [default: .]
  -h, --host TEXT     Host to bind [default: 127.0.0.1]
  -p, --port INTEGER  Port to bind [default: 8000]
  -v, --version       Show version and exit
  --help             Show this message and exit
```

### Development Environment

1. Clone repository:
```bash
git clone [repository-url]
cd fileserver
```

2. Install dependencies:
```bash
poetry install
```

3. Run server:
```bash
poetry run servefs
```

4. Open in browser:
```
http://localhost:8000
```

## Tech Stack

### Backend
- FastAPI: High-performance Python web framework
- Python 3.8+: Programming language
- uvicorn: ASGI server
- Typer: Command-line interface framework
- Rich: Terminal styling

### Frontend
- Vue.js 3: Frontend framework
- Element Plus: UI component library
- @element-plus/icons-vue: Icon library

## Notes

- Files will be automatically renamed to avoid conflicts
- Deletion operations require confirmation
- Supported image formats: jpg, jpeg, png, gif, webp
- File size display automatically converts units (B, KB, MB, GB)

## Development Plan

- [ ] Add file search functionality
- [ ] Support more file type previews
- [ ] Add file sorting functionality
- [ ] Support file renaming
- [ ] Add user authentication
- [ ] Support file sharing
