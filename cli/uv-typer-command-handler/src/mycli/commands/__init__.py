"""Command modules for the CLI."""

from mycli.commands.users import app as users_app
from mycli.commands.demo import app as demo_app

__all__ = ["users_app", "demo_app"]
