"""Keitaro adapter implementing the application port."""

from app import constants
from app.adapters.keitaro.client import KeitaroHttpClient
from app.application.ports import KeitaroGateway


class KeitaroHttpGateway(KeitaroGateway):
    def __init__(self, client: KeitaroHttpClient) -> None:
        self._client = client

    def create_campaign(
        self,
        payload: dict[str, object],
    ) -> dict[str, object]:
        return self._client.post("/campaigns", payload)

    def create_stream(self, payload: dict[str, object]) -> dict[str, object]:
        return self._client.post(constants.KEITARO_STREAMS_PATH, payload)

    #def delete_campaign(self, campaign_id: int) -> None:
     #   self._client.delete(constants.KEITARO_CAMPAIGN_PATH_TEMPLATE.format(campaign_id=campaign_id))

    def close(self) -> None:
        self._client.close()
