from datetime import UTC

import pytest

from app.domain.campaign import Campaign, CampaignName, CampaignStatus, GeoCodes
from app.domain.errors import InvalidOfferId, InvalidStatusTransition


def make_campaign(offer_id: int = 7) -> Campaign:
    return Campaign(
        name=CampaignName("test_ivanov_one"),
        alias="aB3dE9",
        geo=GeoCodes(("MX", "AU")),
        offer_id=offer_id,
    )


def test_a_new_campaign_is_pending_and_has_no_keitaro_id() -> None:
    campaign = make_campaign()

    assert campaign.status is CampaignStatus.PENDING
    assert campaign.keitaro_id is None
    assert campaign.error is None
    assert campaign.id is None
    assert campaign.created_at.tzinfo is UTC


@pytest.mark.parametrize("offer_id", [0, -5])
def test_rejects_a_non_positive_offer_id(offer_id: int) -> None:
    with pytest.raises(InvalidOfferId):
        make_campaign(offer_id)


def test_mark_active_records_the_keitaro_id() -> None:
    campaign = make_campaign()

    campaign.mark_active(keitaro_id=42)

    assert campaign.status is CampaignStatus.ACTIVE
    assert campaign.keitaro_id == 42


def test_mark_failed_records_the_reason() -> None:
    campaign = make_campaign()

    campaign.mark_failed("Keitaro is down")

    assert campaign.status is CampaignStatus.FAILED
    assert campaign.error == "Keitaro is down"


def test_only_a_pending_campaign_can_be_finished() -> None:
    active = make_campaign()
    active.mark_active(keitaro_id=1)
    failed = make_campaign()
    failed.mark_failed("boom")

    with pytest.raises(InvalidStatusTransition, match="active to failed"):
        active.mark_failed("late failure")
    with pytest.raises(InvalidStatusTransition, match="failed to active"):
        failed.mark_active(keitaro_id=2)
