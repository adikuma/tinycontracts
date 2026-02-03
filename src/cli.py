# cli.py - typer entry point
from pathlib import Path

import typer
import uvicorn
from rich import print as rprint

from src.server import create_app

app = typer.Typer(
    name="tinycontracts",
    help="serve a folder of json/csv/parquet files as a rest api",
    no_args_is_help=True,
)


@app.command()
def serve(
    path: str = typer.Argument(..., help="folder containing data files"),
    port: int = typer.Option(4242, "--port", "-p", help="port to serve on"),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="host to bind to"),
):
    folder = Path(path)

    if not folder.exists():
        rprint(f"[red]error:[/red] folder not found: {folder}")
        raise typer.Exit(1)

    if not folder.is_dir():
        rprint(f"[red]error:[/red] not a directory: {folder}")
        raise typer.Exit(1)

    fastapi_app = create_app(folder)
    resources = list(fastapi_app.state.resources.keys()) if hasattr(fastapi_app.state, "resources") else []

    rprint(f"\n[bold cyan]tinycontracts[/bold cyan]")
    rprint(f"[dim]serving {folder}[/dim]\n")
    rprint(f"  [green]→[/green] http://{host}:{port}/")
    rprint(f"  [green]→[/green] http://{host}:{port}/_help")
    rprint(f"  [green]→[/green] http://{host}:{port}/docs\n")

    uvicorn.run(fastapi_app, host=host, port=port, log_level="warning")


if __name__ == "__main__":
    app()
