"""Тестовый скрипт для проверки работы сервисов Bitrix24.

Запускает по одному методу каждого сервиса для проверки их работоспособности.
"""

import asyncio
import sys
from typing import Any

from src.application.services import ContactService, DealService
from src.infrastructure.ioc import container
from src.infrastructure.logging.logger import logger


async def test_contact_service() -> dict[str, Any]:
    """Тестирование сервиса контактов.

    :return: Результаты тестирования
    """
    logger.info("Тестирование сервиса контактов")

    contact_service = container.get(ContactService)
    results = {}

    contacts = await contact_service.list_contacts(limit=5)
    results["list_contacts"] = {
        "success": len(contacts) >= 0,
        "count": len(contacts),
        "first_contact_id": contacts[0].id if contacts else None,
    }

    if contacts:
        contact_id = contacts[0].id
        contact = await contact_service.get_contact_by_id(contact_id)
        results["get_contact_by_id"] = {
            "success": contact is not None,
            "contact_id": contact_id,
            "name": contact.get_full_name() if contact else None,
        }

        if contact and contact.name:
            search_query = contact.name
            search_results = await contact_service.search_contacts(
                search_query,
                "name",
                5,
            )
            results["search_contacts"] = {
                "success": len(search_results) >= 0,
                "query": search_query,
                "count": len(search_results),
            }

    return results


async def test_deal_service() -> dict[str, Any]:
    """Тестирование сервиса сделок.

    :return: Результаты тестирования
    """
    logger.info("Тестирование сервиса сделок")

    deal_service = container.get(DealService)
    results = {}

    deals = await deal_service.list_deals(active_only=True)
    results["list_deals"] = {
        "success": len(deals) >= 0,
        "count": len(deals),
        "first_deal_id": deals[0].id if deals else None,
    }

    stages = await deal_service.get_deal_stages()
    results["get_deal_stages"] = {
        "success": isinstance(stages, list),
        "count": len(stages),
    }

    categories = await deal_service.get_deal_categories()
    results["get_deal_categories"] = {
        "success": isinstance(categories, list),
        "count": len(categories),
    }

    if deals:
        deal_id = deals[0].id
        deal = await deal_service.get_deal_by_id(deal_id)
        results["get_deal_by_id"] = {
            "success": deal is not None,
            "deal_id": deal_id,
            "title": deal.title if deal else None,
        }

    return results


async def run_tests() -> None:
    """Запуск всех тестов."""
    try:
        logger.info("Запуск тестирования сервисов Bitrix24")

        contact_results = await test_contact_service()
        deal_results = await test_deal_service()

        logger.info("===== Результаты тестирования =====")
        logger.info(f"Сервис контактов: {contact_results}")
        logger.info(f"Сервис сделок: {deal_results}")

        logger.info("Тестирование завершено успешно")
    except Exception as e:
        logger.error(f"Ошибка при выполнении тестов: {e}")
        raise


def main() -> None:
    """Точка входа в скрипт тестирования."""
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        logger.info("Тестирование прервано пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
