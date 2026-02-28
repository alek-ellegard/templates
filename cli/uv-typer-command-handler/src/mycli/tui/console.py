"""TUI console module for CLI output."""

import questionary
from questionary import Style
from rich.console import Console
from rich.table import Table

QUESTIONARY_STYLE = Style([
    ("selected", "fg:green noreverse"),
    ("pointer", "fg:green bold"),
    ("highlighted", "bold"),
])

from mycli.domain import User


class TUI:
    """Terminal User Interface for CLI output."""

    def __init__(self) -> None:
        """Initialize TUI with Rich console instances."""
        self.console = Console()
        self.err_console = Console(stderr=True)

    def success(self, message: str) -> None:
        """Display success message with green checkmark.

        Args:
            message: Success message to display
        """
        self.console.print(f"[green]✓[/green] {message}")

    def error(self, message: str) -> None:
        """Display error message with red X to stderr.

        Args:
            message: Error message to display
        """
        self.err_console.print(f"[red]✗[/red] {message}")

    def info(self, message: str) -> None:
        """Display info message with blue info icon.

        Args:
            message: Info message to display
        """
        self.console.print(f"[blue]ℹ[/blue] {message}")

    def user_table(self, users: list[User]) -> None:
        """Display users in a Rich table.

        Args:
            users: List of User objects to display
        """
        table = Table(title="Users")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Email", style="magenta")
        table.add_column("Status", style="green")

        for user in users:
            status_style = "green" if user.status.value == "active" else "yellow"
            table.add_row(
                user.id,
                user.email,
                f"[{status_style}]{user.status.value}[/{status_style}]",
            )

        self.console.print(table)

    def user_detail(self, user: User) -> None:
        """Display detailed information for a single user.

        Args:
            user: User object to display
        """
        self.console.print("[bold]User Details[/bold]")
        self.console.print(f"  ID:     {user.id}")
        self.console.print(f"  Email:  {user.email}")
        status_style = "green" if user.status.value == "active" else "yellow"
        status_value = user.status.value
        self.console.print(
            f"  Status: [{status_style}]{status_value}[/{status_style}]"
        )

    def prompt(self, message: str) -> str:
        """Get user input with a prompt.

        Args:
            message: Prompt message to display

        Returns:
            User input as string
        """
        return input(f"{message} ")

    def confirm(self, message: str) -> bool:
        """Get yes/no confirmation from user.

        Args:
            message: Confirmation message to display

        Returns:
            True if user confirms (y/Y), False otherwise
        """
        response = input(f"{message} [y/N] ").strip().lower()
        return response in ("y", "yes")

    def checkbox(self, message: str, choices: list[str]) -> list[str]:
        """Display a checkbox prompt for multi-select.

        Args:
            message: Prompt message to display
            choices: List of choices to select from

        Returns:
            List of selected choices
        """
        return questionary.checkbox(message, choices=choices, style=QUESTIONARY_STYLE).unsafe_ask()

    def select(self, message: str, choices: list[str]) -> str:
        """Display a select prompt for single-select.

        Args:
            message: Prompt message to display
            choices: List of choices to select from

        Returns:
            Selected choice
        """
        return questionary.select(message, choices=choices, style=QUESTIONARY_STYLE).unsafe_ask()
