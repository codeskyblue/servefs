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

### Command Line

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
  -h, --host TEXT     Host to bind [default: 0.0.0.0]
  -p, --port INTEGER  Port to bind [default: 8000]
  -v, --version       Show version and exit
  --help             Show this message and exit
```

## Development

For development information, please check [Development Guide](DEVELOP.md).

## TODO

- [ ] Support file search
- [ ] Support file rename
- [ ] Add user authentication
- [ ] Support file sharing

## Acknowledgements

- Windsurf
