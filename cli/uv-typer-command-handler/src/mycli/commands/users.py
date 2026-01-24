import typer
from typing import Annotated

from mycli.handlers.users import UserHandler
from mycli.tui.console import TUI

app = typer.Typer(help="User management commands")


def get_handler(ctx: typer.Context) -> UserHandler:
    return ctx.obj["user_handler"]


def get_tui(ctx: typer.Context) -> TUI:
    return ctx.obj["tui"]


@app.command("create")
def create(
    ctx: typer.Context,
    email: Annotated[str, typer.Argument(help="User email address")],
) -> None:
    """Create a new user."""
    handler = get_handler(ctx)
    tui = get_tui(ctx)
    user = handler.create(email)
    tui.success(f"Created user {user.id}")
    tui.user_detail(user)
