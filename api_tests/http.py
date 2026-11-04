import httpx


def make_client(base_url: str, timeout: float) -> httpx.Client:
    # trust_env=False: системный прокси не должен перехватывать запросы к стенду.
    return httpx.Client(base_url=base_url, timeout=timeout, trust_env=False)


def expect_status(response: httpx.Response, expected: int) -> None:
    """Проверяет код ответа. Тело и заголовки не выводятся: в них могут быть токены."""
    if response.status_code != expected:
        raise AssertionError(
            f"{response.request.method} {response.request.url}: "
            f"ожидался HTTP {expected}, получен {response.status_code}"
        )
