"""Small synchronous HTTP client for Keitaro Admin API."""

from typing import Any

import httpx

from app import constants
from app.application.errors import (
    KeitaroAliasConflict,
    KeitaroGatewayError,
)


class KeitaroHttpClient:
    """Talks JSON to the Keitaro Admin API and turns its errors into gateway errors."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            transport=transport,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Api-Key": api_key,
            },
        )

    def post(self, path: str, payload: dict[str, object]) -> dict[str, object]:
        """Send a JSON object and return the JSON object Keitaro answers with."""
        return _expect_object(self._send(constants.HTTP_POST, path, payload))

    def put(self, path: str, payload: dict[str, object]) -> dict[str, object]:
        """Replace a resource and return the updated JSON object."""
        return _expect_object(self._send(constants.HTTP_PUT, path, payload))

    def get_object(self, path: str) -> dict[str, object]:
        """Read a single resource."""
        return _expect_object(self._send(constants.HTTP_GET, path))

    def get_list(self, path: str) -> list[dict[str, object]]:
        """Read a collection (Keitaro answers with a JSON array)."""
        data = self._send(constants.HTTP_GET, path)
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            raise KeitaroGatewayError("Keitaro returned an unexpected response format")
        return data

    def delete(self, path: str) -> None:
        """Delete a resource; an empty response body is fine."""
        self._send(constants.HTTP_DELETE, path)

    def close(self) -> None:
        """Release the underlying HTTP connection pool."""
        self._client.close()

    def _send(
        self,
        method: str,
        path: str,
        payload: dict[str, object] | None = None,
    ) -> Any:
        url = f"{constants.KEITARO_API_PREFIX}{path}"

        try:
            response = self._client.request(method, url, json=payload)
        except httpx.HTTPError as exc:
            raise KeitaroGatewayError(f"Could not connect to Keitaro: {exc}") from exc

        if response.is_error:
            body = response.text

            if method == constants.HTTP_POST and _is_alias_conflict(response.status_code, body):
                raise KeitaroAliasConflict(
                    f"Keitaro rejected campaign alias: {body}",
                    response.status_code,
                )

            raise KeitaroGatewayError(
                f"Keitaro API returned HTTP {response.status_code}: {body}",
                response.status_code,
            )

        if not response.content:
            return None

        try:
            return response.json()
        except ValueError as exc:
            raise KeitaroGatewayError(
                "Keitaro returned a non-JSON response",
                response.status_code,
            ) from exc


def _expect_object(data: Any) -> dict[str, object]:
    if not isinstance(data, dict):
        raise KeitaroGatewayError("Keitaro returned an unexpected response format")
    return data


def _is_alias_conflict(status_code: int, body: str) -> bool:
    normalized = body.lower()

    duplicate_markers = (
        "duplicate",
        "already exists",
        "already been taken",
        "not unique",
    )

    return "alias" in normalized and (
        status_code == constants.HTTP_ALIAS_CONFLICT_STATUS
        or (status_code in (400, 422) and any(marker in normalized for marker in duplicate_markers))
    )
