import os
import sys
from pathlib import Path
from typing import Optional

import typer
import uvicorn
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(
    name="simplehttpserver",
    help="A modern HTTP file server with web UI",
    add_completion=False,
)

console = Console()

def version_callback(value: bool):
    if value:
        from importlib.metadata import version
        try:
            v = version("simplehttpserver")
            console.print(f"[bold]simplehttpserver[/bold] version: {v}")
        except:
            console.print("[bold]simplehttpserver[/bold] version: 0.1.0")
        raise typer.Exit()

def main(
    root: str = ".",
    host: str = "127.0.0.1",
    port: int = 8000,
    version: Optional[bool] = None,
):
    """
    Start the HTTP file server with web UI
    """
    if version:
        version_callback(version)
        return

    # 设置根目录环境变量
    root_path = Path(root).absolute()
    os.environ["FILE_SERVER_ROOT"] = str(root_path)
    
    # 显示服务器信息
    console.print(Panel.fit(
        f"[bold green]Starting server at[/bold green]\n"
        f"[bold]http://{host}:{port}[/bold]\n"
        f"[bold blue]Root directory:[/bold blue] {os.environ['FILE_SERVER_ROOT']}\n"
        "\n[dim]Press Ctrl+C to quit[/dim]",
        title="Simple HTTP Server",
        border_style="blue",
    ))

    # 启动服务器
    uvicorn.run(
        "simplehttpserver.main:app",
        host=host,
        port=port,
        log_level="info",
    )

if __name__ == "__main__":
    typer.run(main)
