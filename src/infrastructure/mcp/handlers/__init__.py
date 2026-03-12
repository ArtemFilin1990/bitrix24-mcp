"""Модуль регистрации обработчиков для компонентов MCP сервера."""

from .contact import register_contact_handlers
from .deal import register_deal_handlers
from .task import register_task_handlers

__all__ = [
    "register_contact_handlers",
    "register_deal_handlers",
    "register_task_handlers",
]
