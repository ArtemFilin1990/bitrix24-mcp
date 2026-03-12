"""Модуль с презентационным слоем MCP сервера.

Отвечает за конфигурацию и запуск MCP сервера для Bitrix24.
"""

from mcp.server.fastmcp import FastMCP

from src.infrastructure.mcp.handlers import (
    register_contact_handlers,
    register_deal_handlers,
    register_task_handlers,
)
from src.infrastructure.mcp.server import BitrixMCPServer


def create_mcp_server() -> FastMCP:
    """Создание и настройка MCP сервера для Bitrix24.

    Регистрирует все обработчики, промпты и инструменты.

    :return: Настроенный экземпляр MCP сервера
    """
    mcp_server = BitrixMCPServer()
    register_contact_handlers(mcp_server)
    register_deal_handlers(mcp_server)
    register_task_handlers(mcp_server)
    return mcp_server.server
