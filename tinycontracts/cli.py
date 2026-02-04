# cli.py - fast startup with lazy imports
import sys


def main():
    # fast path for --help and --version (no heavy imports)
    args = sys.argv[1:]

    if not args or args[0] in ("--help", "-h"):
        print("""tc - serve data files as a rest api

usage: tc <folder> [options]

arguments:
  folder              folder containing json/csv/parquet files

options:
  -p, --port PORT     port to serve on (default: 4242)
  -H, --host HOST     host to bind to (default: 127.0.0.1)
  -v, --version       show version
  -h, --help          show this help""")
        return

    if args[0] in ("--version", "-v"):
        print("tinycontracts v0.1.2")
        return

    # parse args manually for fast path
    path = None
    port = 4242
    host = "127.0.0.1"

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-p", "--port"):
            port = int(args[i + 1])
            i += 2
        elif arg in ("-H", "--host"):
            host = args[i + 1]
            i += 2
        elif arg.startswith("-"):
            print(f"error: unknown option {arg}")
            sys.exit(1)
        else:
            path = arg
            i += 1

    if not path:
        print("error: missing folder path\nusage: tc <folder>")
        sys.exit(1)

    # now import heavy deps
    from pathlib import Path
    from rich.console import Console

    console = Console()
    folder = Path(path)

    if not folder.exists():
        console.print(f"\n  [red]error:[/red] path not found: [bold]{folder}[/bold]")
        console.print("  [dim]make sure the path exists and try again[/dim]\n")
        sys.exit(1)

    if not folder.is_dir():
        console.print(f"\n  [red]error:[/red] not a folder: [bold]{folder}[/bold]")
        console.print("  [dim]tc needs a folder path, not a file[/dim]\n")
        sys.exit(1)

    data_files = (
        list(folder.glob("*.json"))
        + list(folder.glob("*.csv"))
        + list(folder.glob("*.parquet"))
    )
    if not data_files:
        console.print(
            f"\n  [yellow]warning:[/yellow] no data files in [bold]{folder}[/bold]"
        )
        console.print("  [dim]add .json, .csv, or .parquet files[/dim]\n")

    # lazy import heavy deps with spinner
    with console.status("[cyan]loading...[/cyan]", spinner="dots"):
        from tinycontracts.server import create_app
        import uvicorn

        try:
            fastapi_app = create_app(folder)
            resources = (
                list(fastapi_app.state.resources.keys())
                if hasattr(fastapi_app.state, "resources")
                else []
            )
        except PermissionError:
            console.print(f"\n  [red]error:[/red] permission denied: [bold]{folder}[/bold]")
            console.print("  [dim]check file permissions and try again[/dim]\n")
            sys.exit(1)
        except Exception as e:
            console.print(f"\n  [red]error:[/red] failed to load data: {e}\n")
            sys.exit(1)

    # print banner
    from rich.panel import Panel
    from rich.table import Table

    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]tinycontracts[/bold cyan]  [dim]v0.1.2[/dim]",
            border_style="cyan",
        )
    )
    console.print()

    console.print(f"  [dim]folder:[/dim]  {folder.resolve()}")
    console.print(f"  [dim]server:[/dim]  [green]http://{host}:{port}[/green]")
    console.print()

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
        sys.exit(1)


if __name__ == "__main__":
    main()
