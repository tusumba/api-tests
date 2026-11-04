import httpx
import pytest

from api_tests.http import expect_status

pytestmark = pytest.mark.stand


def test_gateway_health(gateway: httpx.Client) -> None:
    response = gateway.get("/health")
    expect_status(response, 200)
    assert response.text.strip() == "ok"


def test_internal_paths_closed(gateway: httpx.Client) -> None:
    # /internal не должен проксироваться наружу.
    response = gateway.get("/internal/events/1/permissions")
    expect_status(response, 404)


def test_unknown_path_not_found(gateway: httpx.Client) -> None:
    response = gateway.get("/v1/no-such-resource")
    expect_status(response, 404)
