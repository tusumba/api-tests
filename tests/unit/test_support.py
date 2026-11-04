import httpx
import pytest
from pydantic import ValidationError

from api_tests.http import expect_status
from api_tests.settings import SERVICE_NAMES, Settings


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("GATEWAY_URL", "SERVICE_URLS", "TIMEOUT_SECONDS"):
        monkeypatch.delenv(f"API_TEST_{name}", raising=False)


def test_defaults_point_to_local_compose() -> None:
    settings = Settings()
    assert str(settings.gateway_url) == "http://localhost:8080/"
    assert str(settings.service_urls["identity"]) == "http://identity:8000/"
    assert set(settings.service_urls) == set(SERVICE_NAMES)


def test_settings_read_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_TEST_GATEWAY_URL", "https://stand.example.com")
    monkeypatch.setenv("API_TEST_SERVICE_URLS", '{"events": "http://localhost:8002"}')
    monkeypatch.setenv("API_TEST_TIMEOUT_SECONDS", "3")
    settings = Settings()
    assert str(settings.gateway_url) == "https://stand.example.com/"
    assert str(settings.service_urls["events"]) == "http://localhost:8002/"
    assert str(settings.service_urls["identity"]) == "http://identity:8000/"
    assert settings.timeout_seconds == 3


@pytest.mark.parametrize("timeout", ["0", "-1", "121", "nan"])
def test_invalid_timeout_rejected(monkeypatch: pytest.MonkeyPatch, timeout: str) -> None:
    monkeypatch.setenv("API_TEST_TIMEOUT_SECONDS", timeout)
    with pytest.raises(ValidationError):
        Settings()


def test_unknown_service_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_TEST_SERVICE_URLS", '{"payments": "http://localhost:8000"}')
    with pytest.raises(ValidationError):
        Settings()


def test_expect_status_hides_body_and_headers() -> None:
    sensitive = "private-test-value"
    response = httpx.Response(
        503,
        text=sensitive,
        request=httpx.Request("GET", "http://nginx/health", headers={"Authorization": sensitive}),
    )
    with pytest.raises(AssertionError) as error:
        expect_status(response, 200)
    assert sensitive not in str(error.value)
    assert "ожидался HTTP 200, получен 503" in str(error.value)
