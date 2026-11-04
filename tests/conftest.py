from collections.abc import Iterator

import httpx
import pytest

from api_tests.http import make_client
from api_tests.settings import Settings


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings()


@pytest.fixture
def gateway(settings: Settings) -> Iterator[httpx.Client]:
    """Клиент шлюза без авторизации, новый на каждый тест."""
    with make_client(str(settings.gateway_url), settings.timeout_seconds) as client:
        yield client
