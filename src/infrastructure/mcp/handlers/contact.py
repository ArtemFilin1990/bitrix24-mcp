"""Модуль с обработчиками MCP для контактов.

Содержит обработчики инструментов и ресурсов для работы с контактами Bitrix24.
"""

import json

from src.domain.entities.contact import Contact

# Create the contact service instance.
# In production these dependencies should come from the DI container.
from src.infrastructure.ioc import provider
from src.infrastructure.logging.logger import logger
from src.infrastructure.mcp.server import BitrixMCPServer

# Получаем зависимости напрямую из провайдера
bitrix_webhook_url = provider.provide_bitrix_webhook_url()
repository_factory = provider.provide_repository_factory()
contact_service = provider.provide_contact_service(repository_factory)


def register_contact_handlers(mcp_server: BitrixMCPServer) -> None:
    """Регистрация обработчиков для работы с контактами.

    :param mcp_server: Экземпляр MCP сервера
    """
    mcp_server.add_tool(
        get_contact,
        name="get_contact",
        description="Получение информации о контакте по ID",
    )

    mcp_server.add_tool(
        search_contacts,
        name="search_contacts",
        description="Поиск контактов по имени, телефону или email",
    )

    mcp_server.add_tool(
        list_contacts,
        name="list_contacts",
        description="Получение списка контактов с возможностью фильтрации",
    )

    mcp_server.add_resource(
        "contact://{contact_id}",
        get_contact_resource,
        description="Получение данных контакта по ID",
    )

    logger.info("Зарегистрированы обработчики для работы с контактами")


async def get_contact(
    contact_id: int,
) -> str:
    """Получение контакта по ID (инструмент).

    :param contact_id: Идентификатор контакта
    :return: JSON-строка с данными контакта или сообщение об ошибке
    """
    contact = await contact_service.get_contact_by_id(contact_id)
    if not contact:
        return json.dumps({"error": f"Контакт с ID={contact_id} не найден"})
    return contact.to_str_json()


async def search_contacts(
    query: str,
    search_type: str = "name",
    limit: int = 10,
) -> str:
    """Поиск контактов (инструмент).

    :param query: Поисковый запрос
    :param search_type: Тип поиска (name, phone, email)
    :param limit: Максимальное количество результатов
    :return: JSON-строка с результатами поиска
    """
    if search_type not in ["name", "phone", "email"]:
        return json.dumps(
            {
                "error": "Недопустимый тип поиска. Используйте: name, phone или email",
            },
        )

    if limit != -1 and limit <= 0:
        return json.dumps(
            {
                "error": "Недопустимое значение limit. Используйте -1 (все элементы) или значение больше 0",
            },
        )

    contacts = await contact_service.search_contacts(query, search_type, limit)

    result = {
        "query": query,
        "search_type": search_type,
        "total": len(contacts),
        "contacts": [json.loads(contact.to_str_json()) for contact in contacts],
    }

    return json.dumps(result)


async def list_contacts(
    limit: int = 50,
    company_id: int | None = None,
) -> str:
    """Получение списка контактов (инструмент).

    :param limit: Максимальное количество результатов
    :param company_id: Идентификатор компании для фильтрации (опционально)
    :return: JSON-строка со списком контактов
    """
    if limit != -1 and limit <= 0:
        return json.dumps(
            {
                "error": "Недопустимое значение limit. Используйте -1 (все элементы) или значение больше 0",
            },
        )

    contacts = await contact_service.list_contacts(limit, company_id)

    filter_info = {}
    if company_id:
        filter_info["company_id"] = company_id

    result = {
        "total": len(contacts),
        "filters": filter_info,
        "contacts": [json.loads(contact.to_str_json()) for contact in contacts],
    }

    return json.dumps(result)


async def get_contact_resource(
    contact_id: str,
) -> str:
    """Получение данных контакта в виде ресурса.

    :param contact_id: Идентификатор контакта
    :return: Строковое представление данных контакта
    """
    try:
        contact_id_int = int(contact_id)
    except ValueError:
        return f"Некорректный ID контакта: {contact_id}"
    contact = await contact_service.get_contact_by_id(contact_id_int)

    if not contact:
        return f"Контакт с ID={contact_id} не найден"

    return _format_contact_for_display(contact)


def _format_contact_for_display(contact: Contact) -> str:
    """Форматирование контакта для читаемого отображения.

    :param contact: Объект контакта
    :return: Форматированная строка с данными контакта
    """
    lines = [
        f"Контакт ID: {contact.id}",
        f"Имя: {contact.get_full_name()}",
        f'Email: {contact.get_primary_email() or "Не указан"}',
        f'Телефон: {contact.get_primary_phone() or "Не указан"}',
        f'Компания ID: {contact.company_id or "Не указана"}',
        f'Ответственный: {contact.assigned_by_id or "Не назначен"}',
        f'Дата создания: {contact.date_create or "Неизвестно"}',
    ]

    return "\n".join(lines)
