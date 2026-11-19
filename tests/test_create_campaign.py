import pytest

from app.application.use_cases.create_campaign import CreateCampaign
from app.domain.campaign import Campaign
from app.domain.errors import CampaignAlreadyExists

PREFIX = "test_d_"
DOMAIN_ID = 1
GROUP_ID = 2
TRAFFIC_SOURCE_ID = 3


class FakeRegistry:
    def __init__(self) -> None:
        self.items: list[Campaign] = []

    def add(self, campaign: Campaign) -> Campaign:
        campaign.id = len(self.items) + 1
        self.items.append(campaign)
        return campaign

    def get(self, campaign_id: int) -> Campaign | None:
        return next((item for item in self.items if item.id == campaign_id), None)

    def save(self, campaign: Campaign) -> None:
        assert campaign in self.items

    def list_all(self) -> list[Campaign]:
        return list(reversed(self.items))


class FakeKeitaro:
    """Records the calls the use case makes to Keitaro."""

    def __init__(self) -> None:
        self.created_campaigns: list[dict[str, object]] = []
        self.created_streams: list[dict[str, object]] = []

    def create_campaign(self, payload: dict[str, object]) -> dict[str, object]:
        self.created_campaigns.append(payload)
        return {"id": 500}

    def create_stream(self, payload: dict[str, object]) -> dict[str, object]:
        self.created_streams.append(payload)
        return {"id": 1}

    def list_streams(self, campaign_id: int) -> list[dict[str, object]]:
        raise NotImplementedError

    def update_stream(self, stream_id: int, payload: dict[str, object]) -> dict[str, object]:
        raise NotImplementedError

    def get_offer(self, offer_id: int) -> dict[str, object]:
        raise NotImplementedError

    def list_offers(self) -> list[dict[str, object]]:
        raise NotImplementedError

    def delete_campaign(self, campaign_id: int) -> None:
        raise NotImplementedError

    def close(self) -> None:
        pass


def _use_case(registry: FakeRegistry, keitaro: FakeKeitaro) -> CreateCampaign:
    return CreateCampaign(
        registry=registry,
        keitaro=keitaro,
        name_prefix=PREFIX,
        domain_id=DOMAIN_ID,
        group_id=GROUP_ID,
        traffic_source_id=TRAFFIC_SOURCE_ID,
    )


def test_creates_a_campaign_and_its_two_streams() -> None:
    registry, keitaro = FakeRegistry(), FakeKeitaro()

    campaign = _use_case(registry, keitaro).execute(name="one", geo="MX,AU", offer_id=7)

    assert campaign.name.value == "test_d_one"
    assert campaign.keitaro_id == 500
    assert len(registry.items) == 1
    assert len(keitaro.created_streams) == 2


def test_a_second_campaign_with_the_same_name_is_rejected() -> None:
    registry, keitaro = FakeRegistry(), FakeKeitaro()
    use_case = _use_case(registry, keitaro)
    use_case.execute(name="one", geo="MX", offer_id=7)

    with pytest.raises(CampaignAlreadyExists, match="test_d_one"):
        use_case.execute(name="one", geo="MX", offer_id=7)

    assert len(registry.items) == 1
    assert len(keitaro.created_campaigns) == 1


def test_the_same_name_with_different_spacing_is_still_the_same_campaign() -> None:
    registry, keitaro = FakeRegistry(), FakeKeitaro()
    use_case = _use_case(registry, keitaro)
    use_case.execute(name="one", geo="MX", offer_id=7)

    with pytest.raises(CampaignAlreadyExists):
        use_case.execute(name=f"  {PREFIX}one  ", geo="MX", offer_id=7)

    assert len(keitaro.created_campaigns) == 1
