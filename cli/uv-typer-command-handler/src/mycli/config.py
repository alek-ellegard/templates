from pathlib import Path

from mycli.handlers.users import UserHandler
from mycli.tui.console import TUI


class AppConfig:
    def __init__(self, data_dir: Path | None = None) -> None:
        if data_dir is None:
            data_dir = Path.home() / ".config" / "mycli"
        self.data_dir = data_dir
        self.users_file = self.data_dir / "users.json"


class AppContext:
    def __init__(
        self,
        config: AppConfig,
        user_handler: UserHandler,
        tui: TUI,
    ) -> None:
        self.config = config
        self.user_handler = user_handler
        self.tui = tui

    def to_dict(self) -> dict:
        return {
            "config": self.config,
            "user_handler": self.user_handler,
            "tui": self.tui,
        }
