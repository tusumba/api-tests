from typing import Literal

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ServiceName = Literal["identity", "events", "ticketing", "moderation", "notifications"]
SERVICE_NAMES: tuple[ServiceName, ...] = (
    "identity",
    "events",
    "ticketing",
    "moderation",
    "notifications",
)


def _default_service_urls() -> dict[ServiceName, AnyHttpUrl]:
    # Имена сервисов в сети Docker Compose из репозитория deploy.
    return {name: AnyHttpUrl(f"http://{name}:8000") for name in SERVICE_NAMES}


class Settings(BaseSettings):
    """Настройки читаются из переменных окружения с префиксом API_TEST_."""

    model_config = SettingsConfigDict(env_prefix="API_TEST_")

    gateway_url: AnyHttpUrl = AnyHttpUrl("http://localhost:8080")
    service_urls: dict[ServiceName, AnyHttpUrl] = Field(default_factory=_default_service_urls)
    timeout_seconds: float = Field(default=10, gt=0, le=120)

    @field_validator("service_urls")
    @classmethod
    def _fill_missing_services(
        cls, value: dict[ServiceName, AnyHttpUrl]
    ) -> dict[ServiceName, AnyHttpUrl]:
        # Можно переопределить адрес одного сервиса, остальные остаются по умолчанию.
        return {**_default_service_urls(), **value}
