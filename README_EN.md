# ServeFS

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

```bash
# Start server with current directory
servefs

# Start server with specific directory
servefs --directory /path/to/files
# or
servefs -d /path/to/files

# Start server on specific port (default: 8000)
servefs --port 8080
# or
servefs -p 8080

# Start server with specific host (default: 0.0.0.0)
servefs --host 127.0.0.1

# Show help
servefs --help
```

### Command Line Options

```
Options:
  -d, --directory TEXT     Root directory to serve [default: .]
  -h, --host TEXT         Server host address [default: 0.0.0.0]
  -p, --port INTEGER      Server port [default: 8000]
  -b, --basic-auth TEXT   Enable basic auth with username:password
  -v, --version          Show version and exit
  --help                 Show this message and exit
```

### Basic Authentication

You can use basic authentication to restrict file access:

```bash
# Set username and password
servefs --basic-auth admin:password123

# Or use the short option
servefs -b admin:password123
```

When basic authentication is enabled:
- Unauthenticated users can only view and download files
- Authenticated users can perform all operations (upload, delete, rename, etc.)
- Authentication is handled through the browser's basic auth mechanism

You can also set authentication through an environment variable:

```bash
export SERVEFS_BASIC_AUTH=admin:password123
servefs
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
