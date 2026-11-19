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

    def list_streams(self, campaign_id: int) -> list[dict[str, object]]:
        return self._client.get_list(
            constants.KEITARO_STREAMS_OF_CAMPAIGN_PATH.format(campaign_id=campaign_id)
        )

    def update_stream(self, stream_id: int, payload: dict[str, object]) -> dict[str, object]:
        return self._client.put(constants.KEITARO_STREAM_PATH.format(stream_id=stream_id), payload)

    def get_offer(self, offer_id: int) -> dict[str, object]:
        return self._client.get_object(constants.KEITARO_OFFER_PATH.format(offer_id=offer_id))

    def list_offers(self) -> list[dict[str, object]]:
        return self._client.get_list(constants.KEITARO_OFFERS_PATH)

    def delete_campaign(self, campaign_id: int) -> None:
        self._client.delete(constants.KEITARO_CAMPAIGN_PATH.format(campaign_id=campaign_id))

    def close(self) -> None:
        self._client.close()

