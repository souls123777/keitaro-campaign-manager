from collections.abc import Callable

import httpx
import pytest

from app.adapters.keitaro.client import KeitaroHttpClient
from app.adapters.keitaro.gateway import KeitaroHttpGateway

API_PREFIX = "/admin_api/v1"


@pytest.fixture
def capture() -> tuple[list[httpx.Request], httpx.MockTransport]:
    """Keeps the requests the gateway sends instead of sending them to Keitaro."""
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "GET" and request.url.path.endswith(("/offers", "/streams")):
            return httpx.Response(200, json=[])
        return httpx.Response(200, json={"id": 1})

    return requests, httpx.MockTransport(handler)


def _gateway(transport: httpx.MockTransport) -> KeitaroHttpGateway:
    client = KeitaroHttpClient(
        base_url="https://keitaro.example.com",
        api_key="key",
        transport=transport,
    )
    return KeitaroHttpGateway(client)


@pytest.mark.parametrize(
    ("call", "method", "path"),
    [
        (lambda gw: gw.create_campaign({"name": "x"}), "POST", "/campaigns"),
        (lambda gw: gw.create_stream({"campaign_id": 5}), "POST", "/streams"),
        (lambda gw: gw.list_streams(5), "GET", "/campaigns/5/streams"),
        (lambda gw: gw.update_stream(7, {"name": "x"}), "PUT", "/streams/7"),
        (lambda gw: gw.get_offer(3), "GET", "/offers/3"),
        (lambda gw: gw.list_offers(), "GET", "/offers"),
        (lambda gw: gw.delete_campaign(9), "DELETE", "/campaigns/9"),
    ],
)
def test_every_operation_uses_the_admin_api_path(
    capture: tuple[list[httpx.Request], httpx.MockTransport],
    call: Callable[[KeitaroHttpGateway], object],
    method: str,
    path: str,
) -> None:
    requests, transport = capture

    call(_gateway(transport))

    request = requests[-1]
    assert request.method == method
    assert request.url.path == API_PREFIX + path
    assert "{" not in str(request.url)
