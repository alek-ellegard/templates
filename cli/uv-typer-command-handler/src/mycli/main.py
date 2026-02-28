import typer
from pathlib import Path
from typing import Annotated

from mycli.config import AppConfig, AppContext
from mycli.repository.json import JsonUserRepository
from mycli.handlers.users import UserHandler
from mycli.tui.console import TUI
from mycli.commands import users, demo
from mycli.exceptions import CLIError

app = typer.Typer(
    name="mycli",
    help="A modern CLI template",
    no_args_is_help=True,
)

app.add_typer(users.app, name="users")
app.add_typer(demo.app, name="demo")


@app.callback()
def main(
    ctx: typer.Context,
    data_dir: Annotated[
        Path | None,
        typer.Option("--data-dir", "-d", help="Data directory path"),
    ] = None,
) -> None:
    """Initialize application context."""
    config = AppConfig(data_dir)
    repository = JsonUserRepository(config.users_file)
    handler = UserHandler(repository)
    tui = TUI()
    context = AppContext(config, handler, tui)
    ctx.obj = context.to_dict()


def run() -> None:
    try:
        app()
    except CLIError as e:
        tui = TUI()
        tui.error(e.message)
        raise typer.Exit(e.exit_code)


if __name__ == "__main__":
    run()
