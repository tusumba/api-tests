# api-tests

Автотесты API Tusumba для стенда.

**Ответственный:** Михаил Николаев (каркас автотестов, задача #18903). Тест-стратегия и шаблоны тест-кейсов: Кирилл Колосов (#18902).

## Что делает

Проверяет внешний API (`/v1/...`) на тестовом стенде по OpenAPI-контрактам сервисов. Баги заводятся в Redmine трекером Bug.

Сейчас в наборе smoke-тесты:

| Тест | Что проверяет |
|---|---|
| `tests/smoke/test_gateway.py` | шлюз отвечает: `GET /health` → 200 `ok`; `/internal/...` и неизвестные пути → 404 |
| `tests/smoke/test_services.py` | `GET /health` каждого из пяти сервисов → 200 `{"status": "ok"}` |

## Запуск

Нужны Git и Docker с Compose v2. Для запуска без Docker и для разработки тестов ещё нужен [uv](https://docs.astral.sh/uv/).

### Против docker compose (основной способ)

1. Поднимите стенд по [README репозитория deploy](https://github.com/tusumba/deploy#запуск):

   ```bash
   docker compose up -d --build --wait
   ```

2. Из корня `api-tests` запустите тесты одной командой:

   ```bash
   docker compose run --build --rm api-tests
   ```

Контейнер с тестами подключается к сети стенда `tusumba_default`. Шлюз внутри сети доступен по `http://nginx`, сервисы — по `http://<имя>:8000`. Так проверяется и `/health` сервисов, который шлюз наружу не отдаёт. Стенд эта команда не поднимает и не останавливает.

Аргументы после `api-tests` передаются в pytest, например только тесты шлюза:

```bash
docker compose run --build --rm api-tests -v tests/smoke/test_gateway.py
```

### Локально, без Docker

```bash
uv sync
uv run pytest -m "not in_network"
```

С хоста видно только шлюз (по умолчанию `http://localhost:8080`), поэтому тесты с меткой `in_network` (прямые запросы к сервисам) пропускаются фильтром `-m`. Если запустить их без фильтра, они упадут: имена `identity`, `events` и т. д. с хоста не резолвятся.

### Против удалённого стенда

Адрес стенда задаётся переменной `API_TEST_GATEWAY_URL`:

```bash
API_TEST_GATEWAY_URL=https://<адрес стенда> uv run pytest -m "not in_network"
```

В PowerShell: `$env:API_TEST_GATEWAY_URL = "https://<адрес стенда>"`, затем `uv run pytest -m "not in_network"`.

### Настройки

Читаются из переменных окружения (pydantic-settings, префикс `API_TEST_`). Файл `.env` не читается.

| Переменная | По умолчанию | Что это |
|---|---|---|
| `API_TEST_GATEWAY_URL` | `http://localhost:8080`, в контейнере `http://nginx` | адрес шлюза стенда |
| `API_TEST_SERVICE_URLS` | `http://<имя>:8000` для каждого сервиса | JSON с адресами сервисов, например `{"events": "http://localhost:8002"}`; не указанные сервисы остаются по умолчанию |
| `API_TEST_TIMEOUT_SECONDS` | `10` | таймаут HTTP-запроса, от 0 до 120 |
| `API_TEST_NETWORK` | `tusumba_default` | сеть Docker стенда, только для `docker compose run` |

### Метки pytest

| Метка | Значение |
|---|---|
| `stand` | нужен запущенный стенд |
| `in_network` | нужен прямой доступ к сервисам, работает только в контейнере внутри сети стенда |

Без меток — тесты самого каркаса, стенд им не нужен. Их и линтеры запускает CI:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy api_tests tests
uv run pytest -m "not stand"
```

## Как добавить тест

- Тесты лежат в `tests/`, общие фикстуры — в `tests/conftest.py`, вспомогательный код — в пакете `api_tests/`.
- Фикстура `gateway` — `httpx.Client` с адресом шлюза, отдельный на каждый тест; `settings` — настройки запуска.
- Код ответа проверяйте через `api_tests.http.expect_status`: при ошибке он не печатает тело и заголовки, в которых бывают токены.
- Тест, которому нужен стенд, помечайте `@pytest.mark.stand`.

```python
import httpx
import pytest

from api_tests.http import expect_status


@pytest.mark.stand
def test_events_catalog(gateway: httpx.Client) -> None:
    response = gateway.get("/v1/events")
    expect_status(response, 200)
    assert "items" in response.json()
```

## Стек

Python 3.12, uv, pytest, httpx, pydantic-settings; ruff и mypy.

## Документация

Wiki проекта: https://ai.nsu.ru/projects/tusumba/wiki/Архитектура. Задачи ведутся в Redmine: https://ai.nsu.ru/projects/tusumba. Issues и Wiki GitHub выключены.

## Правила работы

Ветки, коммиты, pull request и code review описаны в [CONTRIBUTING.md](https://github.com/tusumba/.github/blob/main/CONTRIBUTING.md). Коротко:

- ветка называется `feature/<номер задачи Redmine>-<пара слов>`, например `feature/18901-login`;
- номер задачи указывается в каждом коммите и в названии PR;
- в `main` изменения попадают только через PR с одним одобрением и зелёным CI, прямой push и force push запрещены.
