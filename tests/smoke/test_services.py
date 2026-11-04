import pytest

from api_tests.http import expect_status, make_client
from api_tests.settings import SERVICE_NAMES, ServiceName, Settings

# /health сервисов шлюз не проксирует, поэтому тесты ходят к сервисам напрямую.
pytestmark = [pytest.mark.stand, pytest.mark.in_network]


@pytest.mark.parametrize("service", SERVICE_NAMES)
def test_service_health(settings: Settings, service: ServiceName) -> None:
    url = str(settings.service_urls[service])
    with make_client(url, settings.timeout_seconds) as client:
        response = client.get("/health")
    expect_status(response, 200)
    assert response.json() == {"status": "ok"}
