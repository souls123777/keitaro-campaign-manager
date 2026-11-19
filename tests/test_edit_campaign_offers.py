import copy

import pytest

from app.application.use_cases.edit_campaign_offers import (
    CampaignNotEditable,
    EditCampaignOffers,
    OfferStreamNotFound,
)
from app.domain.campaign import Campaign, CampaignName, GeoCodes
from app.domain.errors import (
    CampaignNotFound,
    LastOfferRemoval,
    OfferAlreadyInCampaign,
)

KEITARO_CAMPAIGN_ID = 500
OFFER_STREAM_ID = 11


class FakeRegistry:
    def __init__(self) -> None:
        self.items: dict[int, Campaign] = {}

    def add(self, campaign: Campaign) -> Campaign:
        campaign.id = len(self.items) + 1
        self.items[campaign.id] = campaign
        return campaign

    def get(self, campaign_id: int) -> Campaign | None:
        return self.items.get(campaign_id)

    def save(self, campaign: Campaign) -> None:
        assert campaign.id is not None
        self.items[campaign.id] = campaign

    def list_all(self) -> list[Campaign]:
        return list(self.items.values())


class FakeKeitaro:
    """Keeps streams in memory and applies updates the way Keitaro does."""

    def __init__(self, offers_in_stream: list[int]) -> None:
        self.known_offers = {1: "One", 2: "Two", 3: "Three", 4: "Four"}
        self.updates: list[dict[str, object]] = []
        self.streams: list[dict[str, object]] = [
            {"id": 10, "schema": "redirect", "offers": [], "created_at": "x"},
            {
                "id": OFFER_STREAM_ID,
                "schema": "landings",
                "created_at": "x",
                "offers": [
                    {"offer_id": offer_id, "share": 0, "state": "active"}
                    for offer_id in offers_in_stream
                ],
            },
        ]

    def create_campaign(self, payload: dict[str, object]) -> dict[str, object]:
        raise NotImplementedError

    def create_stream(self, payload: dict[str, object]) -> dict[str, object]:
        raise NotImplementedError

    def list_streams(self, campaign_id: int) -> list[dict[str, object]]:
        assert campaign_id == KEITARO_CAMPAIGN_ID
        return copy.deepcopy(self.streams)

    def update_stream(self, stream_id: int, payload: dict[str, object]) -> dict[str, object]:
        self.updates.append(payload)
        for stream in self.streams:
            if stream["id"] == stream_id:
                stream["offers"] = payload["offers"]
        return {}

    def get_offer(self, offer_id: int) -> dict[str, object]:
        if offer_id not in self.known_offers:
            raise LookupError(offer_id)
        return {"id": offer_id, "name": self.known_offers[offer_id]}

    def list_offers(self) -> list[dict[str, object]]:
        return [{"id": key, "name": value} for key, value in self.known_offers.items()]

    def delete_campaign(self, campaign_id: int) -> None:
        raise NotImplementedError


def _setup(offers: list[int]) -> tuple[EditCampaignOffers, FakeKeitaro, int]:
    registry = FakeRegistry()
    campaign = Campaign(
        name=CampaignName.create("x", "test_d_"),
        alias="abc12345",
        geo=GeoCodes.parse("AU"),
        offer_id=1,
    )
    campaign.mark_active(KEITARO_CAMPAIGN_ID)
    registry.add(campaign)
    keitaro = FakeKeitaro(offers)
    assert campaign.id is not None
    return EditCampaignOffers(registry, keitaro), keitaro, campaign.id


def test_view_lists_offers_with_names() -> None:
    editor, _, campaign_id = _setup([1, 2])
    result = editor.view(campaign_id)
    assert [(line.offer_id, line.name) for line in result.offers] == [(1, "One"), (2, "Two")]


def test_add_offer_splits_traffic_evenly() -> None:
    editor, keitaro, campaign_id = _setup([1])
    result = editor.add_offer(campaign_id, 2)
    assert [(line.offer_id, line.share) for line in result.offers] == [(1, 50), (2, 50)]
    payload = keitaro.updates[0]
    assert "id" not in payload and "created_at" not in payload
    assert payload["schema"] == "landings"


def test_add_third_offer_gives_remainder_to_first() -> None:
    editor, _, campaign_id = _setup([1, 2])
    result = editor.add_offer(campaign_id, 3)
    assert [line.share for line in result.offers] == [34, 33, 33]
    assert sum(line.share for line in result.offers) == 100


def test_remove_offer_rebalances() -> None:
    editor, _, campaign_id = _setup([1, 2, 3])
    result = editor.remove_offer(campaign_id, 2)
    assert [(line.offer_id, line.share) for line in result.offers] == [(1, 50), (3, 50)]


def test_cannot_remove_last_offer() -> None:
    editor, keitaro, campaign_id = _setup([1])
    with pytest.raises(LastOfferRemoval):
        editor.remove_offer(campaign_id, 1)
    assert keitaro.updates == []


def test_duplicate_offer_is_rejected_without_calling_keitaro() -> None:
    editor, keitaro, campaign_id = _setup([1])
    with pytest.raises(OfferAlreadyInCampaign):
        editor.add_offer(campaign_id, 1)
    assert keitaro.updates == []


def test_unknown_offer_is_not_added() -> None:
    editor, keitaro, campaign_id = _setup([1])
    with pytest.raises(LookupError):
        editor.add_offer(campaign_id, 999)
    assert keitaro.updates == []


def test_unknown_campaign() -> None:
    editor, _, _ = _setup([1])
    with pytest.raises(CampaignNotFound):
        editor.view(12345)


def test_pending_campaign_is_not_editable() -> None:
    registry = FakeRegistry()
    pending = registry.add(
        Campaign(
            name=CampaignName.create("x", "test_d_"),
            alias="abc12345",
            geo=GeoCodes.parse("AU"),
            offer_id=1,
        )
    )
    editor = EditCampaignOffers(registry, FakeKeitaro([1]))
    assert pending.id is not None
    with pytest.raises(CampaignNotEditable):
        editor.view(pending.id)


def test_campaign_without_offer_stream() -> None:
    editor, keitaro, campaign_id = _setup([1])
    keitaro.streams = [{"id": 10, "schema": "redirect", "offers": []}]
    with pytest.raises(OfferStreamNotFound):
        editor.view(campaign_id)


def test_search_by_name_is_case_insensitive() -> None:
    editor, _, _ = _setup([1])
    assert [item.id for item in editor.search_offers("TWO")] == [2]


def test_search_by_id_prefix() -> None:
    editor, _, _ = _setup([1])
    assert [item.id for item in editor.search_offers("3")] == [3]


def test_search_respects_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    editor, _, _ = _setup([1])
    monkeypatch.setattr("app.constants.OFFER_SEARCH_LIMIT", 2)
    assert len(editor.search_offers("o")) == 2
