"""MCP обработчики для задач Bitrix24."""

import json
from typing import Any

from fast_bitrix24 import Bitrix

from src.config import SettingsManager
from src.infrastructure.logging.logger import logger
from src.infrastructure.mcp.server import BitrixMCPServer

bitrix_client = Bitrix(SettingsManager.get().BITRIX_WEBHOOK_URL)


def register_task_handlers(mcp_server: BitrixMCPServer) -> None:
    """Регистрация MCP-инструментов для работы с задачами."""
    mcp_server.add_tool(
        create_task,
        name="create_task",
        description="Создание новой задачи в Bitrix24",
    )
    mcp_server.add_tool(
        list_tasks,
        name="list_tasks",
        description="Получение списка задач по фильтру",
    )
    logger.info("Зарегистрированы обработчики для работы с задачами")


async def create_task(
    title: str,
    description: str = "",
    responsible_id: int | None = None,
    deadline: str | None = None,
    accomplices: list[int] | None = None,
) -> str:
    """Создать задачу в Bitrix24.

    :param title: Название задачи
    :param description: Описание задачи
    :param responsible_id: ID ответственного пользователя Bitrix24
    :param deadline: Дедлайн в формате Bitrix (например, 2026-03-31T18:00:00+03:00)
    :param accomplices: Список ID соисполнителей
    :return: JSON-строка с результатом создания
    """
    clean_title = title.strip()
    if not clean_title:
        return json.dumps({"error": "Параметр title не может быть пустым"})

    fields: dict[str, Any] = {"TITLE": clean_title}

    clean_description = description.strip()
    if clean_description:
        fields["DESCRIPTION"] = clean_description

    if responsible_id is not None:
        if responsible_id <= 0:
            return json.dumps({"error": "responsible_id должен быть больше 0"})
        fields["RESPONSIBLE_ID"] = responsible_id

    if deadline is not None:
        clean_deadline = deadline.strip()
        if not clean_deadline:
            return json.dumps({"error": "deadline не может быть пустым"})
        fields["DEADLINE"] = clean_deadline

    accomplice_ids = _validate_positive_ids(accomplices, "accomplices")
    if accomplice_ids is None:
        return json.dumps(
            {"error": "accomplices должен содержать только положительные ID"},
        )
    if accomplice_ids:
        fields["ACCOMPLICES"] = accomplice_ids

    try:
        response = await bitrix_client.call("tasks.task.add", {"fields": fields})
    except Exception as exc:
        logger.error(f"Ошибка при создании задачи: {exc}")
        return json.dumps({"error": "Не удалось создать задачу"})

    task_id = _extract_task_id(response)
    return json.dumps(
        {
            "success": task_id is not None,
            "task_id": task_id,
            "raw_result": response,
        },
        ensure_ascii=False,
    )


async def list_tasks(
    limit: int = 20,
    filter_status: int | None = None,
    filter_responsible_id: int | None = None,
) -> str:
    """Получить список задач из Bitrix24.

    :param limit: Максимальное количество задач (>0)
    :param filter_status: Статус задачи для фильтрации
    :param filter_responsible_id: ID ответственного для фильтрации
    :return: JSON-строка со списком задач
    """
    if limit <= 0:
        return json.dumps({"error": "limit должен быть больше 0"})

    task_filter: dict[str, Any] = {}

    if filter_status is not None:
        task_filter["STATUS"] = filter_status

    if filter_responsible_id is not None:
        if filter_responsible_id <= 0:
            return json.dumps({"error": "filter_responsible_id должен быть больше 0"})
        task_filter["RESPONSIBLE_ID"] = filter_responsible_id

    params: dict[str, Any] = {
        "order": {"ID": "desc"},
        "select": ["ID", "TITLE", "STATUS", "RESPONSIBLE_ID", "DEADLINE"],
        "filter": task_filter,
    }

    try:
        response = await bitrix_client.call("tasks.task.list", params)
    except Exception as exc:
        logger.error(f"Ошибка при получении списка задач: {exc}")
        return json.dumps({"error": "Не удалось получить список задач"})

    tasks = _extract_tasks(response)
    return json.dumps(
        {
            "total": len(tasks[:limit]),
            "tasks": tasks[:limit],
            "raw_result": response,
        },
        ensure_ascii=False,
    )


def _validate_positive_ids(ids: list[int] | None, field_name: str) -> list[int] | None:
    """Проверить, что список содержит только положительные целые ID."""
    if ids is None:
        return []

    try:
        clean_ids = [int(item) for item in ids]
    except (TypeError, ValueError):
        logger.warning(f"Некорректные данные в {field_name}: {ids}")
        return None

    if any(item <= 0 for item in clean_ids):
        logger.warning(f"Неположительные значения в {field_name}: {ids}")
        return None

    return clean_ids


def _extract_task_id(response: Any) -> int | None:
    """Извлечь ID задачи из ответа Bitrix24."""
    if not isinstance(response, dict):
        return None

    result = response.get("result")
    if isinstance(result, int):
        return result

    if isinstance(result, dict):
        task = result.get("task")
        if isinstance(task, dict):
            task_id = task.get("id")
            if isinstance(task_id, str) and task_id.isdigit():
                return int(task_id)
            if isinstance(task_id, int):
                return task_id

    return None


def _extract_tasks(response: Any) -> list[dict[str, Any]]:
    """Извлечь массив задач из ответа Bitrix24."""
    if not isinstance(response, dict):
        return []

    result = response.get("result")
    if not isinstance(result, dict):
        return []

    tasks = result.get("tasks")
    if not isinstance(tasks, list):
        return []

    return [task for task in tasks if isinstance(task, dict)]
