"""Repository layer for data persistence."""

from mycli.repository.base import UserRepository
from mycli.repository.json import JsonUserRepository

__all__ = ["UserRepository", "JsonUserRepository"]
