import typer
from pathlib import Path
from typing import Annotated

from mycli.handlers import UserHandler
from mycli.repository import JsonUserRepository
from mycli.tui import TUI
from mycli.exceptions import CLIError

app = typer.Typer(help="User management commands")


def get_handler(ctx: typer.Context) -> UserHandler:
    """Get UserHandler with configured repository.

    Args:
        ctx: Typer context containing obj dict with repo_path

    Returns:
        Configured UserHandler instance
    """
    repo_path = ctx.obj.get("repo_path", Path.home() / ".mycli" / "users.json")
    repo = JsonUserRepository(repo_path)
    return UserHandler(repo)


def get_tui(ctx: typer.Context) -> TUI:
    """Get TUI instance from context.

    Args:
        ctx: Typer context containing obj dict with optional tui

    Returns:
        TUI instance for output
    """
    return ctx.obj.get("tui", TUI())


@app.command("create")
def create(
    ctx: typer.Context,
    email: Annotated[str, typer.Argument(help="User email address")]
) -> None:
    """Create a new user."""
    handler = get_handler(ctx)
    tui = get_tui(ctx)

    try:
        user = handler.create(email)
        tui.success(f"Created user {user.id}")
        tui.user_detail(user)
    except CLIError as e:
        tui.error(e.message)
        raise typer.Exit(code=e.exit_code)


@app.command("list")
def list_users(ctx: typer.Context) -> None:
    """List all users."""
    handler = get_handler(ctx)
    tui = get_tui(ctx)
    users = handler.list()
    if not users:
        tui.info("No users found")
        return
    tui.user_table(users)


@app.command("get")
def get(
    ctx: typer.Context,
    user_id: Annotated[str, typer.Argument(help="User ID")],
) -> None:
    """Get user by ID."""
    handler = get_handler(ctx)
    tui = get_tui(ctx)
    user = handler.get(user_id)
    tui.user_detail(user)


@app.command("delete")
def delete(
    ctx: typer.Context,
    user_id: Annotated[str, typer.Argument(help="User ID")],
    force: Annotated[bool, typer.Option("--force", "-f", help="Skip confirmation")] = False,
) -> None:
    """Delete a user."""
    handler = get_handler(ctx)
    tui = get_tui(ctx)
    if not force:
        if not tui.confirm(f"Delete user {user_id}?"):
            tui.info("Cancelled")
            raise typer.Exit(0)
    handler.delete(user_id)
    tui.success(f"Deleted user {user_id}")
