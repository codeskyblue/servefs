import os
from pathlib import Path
from typing import Optional

import typer
import uvicorn
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(
    name="servefs",
    help="A modern HTTP file server with web UI",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()

def version_callback(value: bool):
    """Display version information"""
    if value:
        from importlib.metadata import version
        try:
            v = version("servefs")
            console.print(f"[bold]servefs[/bold] version: {v}")
        except:
            console.print("[bold]servefs[/bold] version: 0.0.0")
        raise typer.Exit()

@app.command(help="Start the HTTP file server")
def main(
    root: Path = typer.Option(
        Path("."),
        "--root",
        "-r",
        help="Root directory path, defaults to current directory",
        exists=True,
        dir_okay=True,
        file_okay=False,
    ),
    port: int = typer.Option(
        8000,
        "--port",
        "-p",
        help="Server port, defaults to 8000",
        min=1,
        max=65535,
    ),
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        help="Server host address, defaults to 127.0.0.1",
    ),
    reload: bool = typer.Option(
        False,
        "--reload",
        help="Enable developer mode with automatic code reloading",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version information",
        is_eager=True,
        callback=version_callback,
    ),
):
    """
    A modern HTTP file server with web UI

    Features:
    - File upload and download
    - File preview (supports images and text files)
    - File management (delete, rename, etc.)
    - Beautiful web interface
    """
    # Set root directory environment variable
    root_path = root.absolute()
    os.environ["FILE_SERVER_ROOT"] = str(root_path)
    
    # Display server information
    console.print(Panel.fit(
        f"[bold green]Starting server at[/bold green]\n"
        f"[bold]http://{host}:{port}[/bold]\n"
        f"[bold blue]Root directory:[/bold blue] {os.environ['FILE_SERVER_ROOT']}\n"
        f"[bold yellow]Developer mode:[/bold yellow] {'enabled' if reload else 'disabled'}\n"
        "\n[dim]Press Ctrl+C to quit[/dim]",
        title="Web File Server",
        border_style="blue",
    ))

    # Start the server
    uvicorn.run(
        "servefs.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )

if __name__ == "__main__":
    app()
