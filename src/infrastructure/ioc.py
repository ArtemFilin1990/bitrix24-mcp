"""Модуль с контейнером зависимостей приложения.

Предоставляет единую точку инициализации и получения зависимостей.
"""

from dishka import Provider, Scope, make_container, provide
from fast_bitrix24 import Bitrix

from src.application.services.contact import ContactService
from src.application.services.deal import DealService
from src.config import SettingsManager
from src.infrastructure.bitrix.bitrix_contact_repository import BitrixContactRepository
from src.infrastructure.bitrix.bitrix_deal_repository import BitrixDealRepository
from src.infrastructure.bitrix.repository_factory import BitrixRepositoryFactory
from src.infrastructure.logging.logger import logger
from src.infrastructure.mcp.server import BitrixMCPServer


class DependencyProvider(Provider):
    """Главный провайдер зависимостей приложения."""

    def __init__(self) -> None:
        super().__init__()
        self.bitrix_webhook_url = SettingsManager.get().BITRIX_WEBHOOK_URL

    @provide(scope=Scope.APP)
    def provide_bitrix_webhook_url(self) -> str:
        """Предоставляет URL вебхука Bitrix."""
        return self.bitrix_webhook_url

    @provide(scope=Scope.APP)
    def provide_repository_factory(self) -> BitrixRepositoryFactory:
        """Создание фабрики репозиториев Bitrix24.

        :return: Экземпляр фабрики репозиториев
        """
        bitrix_client = Bitrix(self.bitrix_webhook_url)
        logger.info("Инициализация фабрики репозиториев Bitrix24")
        contact_repository = BitrixContactRepository(bitrix_client)
        return BitrixRepositoryFactory(
            [
                contact_repository,
                BitrixDealRepository(bitrix_client, contact_repository),
            ],
        )

    @provide(scope=Scope.APP)
    def provide_mcp_server(self) -> BitrixMCPServer:
        """Предоставляет сервер MCP."""
        return BitrixMCPServer()

    @provide(scope=Scope.APP)
    def provide_contact_service(self, repository_factory: BitrixRepositoryFactory) -> ContactService:
        """Предоставляет сервис для работы с контактами."""
        return ContactService(repository_factory)

    @provide(scope=Scope.APP)
    def provide_deal_service(self, repository_factory: BitrixRepositoryFactory) -> DealService:
        """Предоставляет сервис для работы со сделками."""
        return DealService(repository_factory)


provider = DependencyProvider()
container = make_container(provider)
