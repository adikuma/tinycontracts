# cli.py - typer entry point
import sys
from pathlib import Path

import typer
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from tinycontracts.server import create_app

console = Console()

app = typer.Typer(
    name="tc",
    help="serve a folder of json/csv/parquet files as a rest api",
    no_args_is_help=True,
    add_completion=False,
)


def print_banner(host: str, port: int, resources: list[str], folder: Path):
    # header
    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]tinycontracts[/bold cyan]  [dim]v0.1.1[/dim]",
            border_style="cyan",
        )
    )
    console.print()

    # server info
    console.print(f"  [dim]folder:[/dim]  {folder.resolve()}")
    console.print(f"  [dim]server:[/dim]  [green]http://{host}:{port}[/green]")
    console.print()

    # endpoints table
    if resources:
        table = Table(show_header=True, header_style="bold", box=None, padding=(0, 2))
        table.add_column("endpoint", style="green")
        table.add_column("description", style="dim")

        for name in sorted(resources):
            table.add_row(f"/{name}", f"query {name}")

        table.add_row("", "")
        table.add_row("/docs", "swagger ui")
        table.add_row("/_help", "api help")

        console.print(table)
    else:
        console.print("  [yellow]no data files found[/yellow]")

    console.print()
    console.print("  [dim]press ctrl+c to stop[/dim]")
    console.print()


@app.command()
def serve(
    path: str = typer.Argument(..., help="folder containing data files"),
    port: int = typer.Option(4242, "--port", "-p", help="port to serve on"),
    host: str = typer.Option("127.0.0.1", "--host", "-H", help="host to bind to"),
):
    """serve data files as a rest api"""
    folder = Path(path)

    # validate folder exists
    if not folder.exists():
        console.print(f"\n  [red]error:[/red] path not found: [bold]{folder}[/bold]")
        console.print(f"  [dim]make sure the path exists and try again[/dim]\n")
        raise typer.Exit(1)

    # validate it's a directory
    if not folder.is_dir():
        console.print(f"\n  [red]error:[/red] not a folder: [bold]{folder}[/bold]")
        console.print(f"  [dim]tc needs a folder path, not a file[/dim]\n")
        raise typer.Exit(1)

    # check for data files
    data_files = (
        list(folder.glob("*.json"))
        + list(folder.glob("*.csv"))
        + list(folder.glob("*.parquet"))
    )
    if not data_files:
        console.print(
            f"\n  [yellow]warning:[/yellow] no data files in [bold]{folder}[/bold]"
        )
        console.print("[dim]add .json, .csv, or .parquet files[/dim]\n")

    # create app
    try:
        fastapi_app = create_app(folder)
        resources = (
            list(fastapi_app.state.resources.keys())
            if hasattr(fastapi_app.state, "resources")
            else []
        )
    except PermissionError:
        console.print(f"\n  [red]error:[/red] permission denied: [bold]{folder}[/bold]")
        console.print("[dim]check file permissions and try again[/dim]\n")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n  [red]error:[/red] failed to load data: {e}\n")
        raise typer.Exit(1)

    # print startup banner
    print_banner(host, port, resources, folder)

    # run server
    try:
        uvicorn.run(fastapi_app, host=host, port=port, log_level="warning")
    except KeyboardInterrupt:
        console.print("\n  [dim]stopped[/dim]\n")
    except OSError as e:
        if "address already in use" in str(e).lower() or "10048" in str(e):
            console.print(f"\n  [red]error:[/red] port {port} already in use")
            console.print(f"  [dim]try: tc {path} -p {port + 1}[/dim]\n")
        else:
            console.print(f"\n  [red]error:[/red] {e}\n")
        raise typer.Exit(1)


@app.command()
def version():
    """show version"""
    console.print("tinycontracts [cyan]v0.1.1[/cyan]")


if __name__ == "__main__":
    app()
