import inspect
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
        "--directory",
        "-d",
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
        "0.0.0.0",
        "--host",
        help="Server host address, defaults to 0.0.0.0",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable developer mode with /docs and /redoc support",
    ),
    basic_auth: Optional[str] = typer.Option(
        None,
        "--basic-auth",
        "-b",
        help="Basic auth credentials in format username:password",
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
    os.environ["SERVEFS_ROOT"] = str(root_path)
    os.environ["SERVEFS_DEBUG"] = "true" if debug else "false"
    if basic_auth:
        os.environ["SERVEFS_BASIC_AUTH"] = basic_auth
    
    # Display server information
    console.print(Panel.fit(
        f"[bold green]Starting server at[/bold green]\n"
        f"[bold]http://{host}:{port}[/bold]\n"
        f"[bold blue]Root directory:[/bold blue] {os.environ['SERVEFS_ROOT']}\n"
        f"[bold yellow]Developer mode:[/bold yellow] {'enabled' if debug else 'disabled'}\n"
        "\n[dim]Press Ctrl+C to quit[/dim]",
        title="Web File Server",
        border_style="blue",
    ))

    # Start the server
    uvicorn.run(
        "servefs.main:app",
        host=host,
        port=port,
        log_level="info",
    )

if __name__ == "__main__":
    app()
