import pytest

from app import constants
from app.domain.campaign import CampaignName
from app.domain.errors import InvalidCampaignName

PREFIX = "test_ivanov_"


def test_adds_the_prefix() -> None:
    assert CampaignName.create("campaign1", PREFIX).value == "test_ivanov_campaign1"


def test_does_not_double_an_existing_prefix() -> None:
    assert CampaignName.create("test_ivanov_campaign1", PREFIX).value == "test_ivanov_campaign1"


def test_strips_surrounding_whitespace() -> None:
    assert CampaignName.create("  campaign1 \n", PREFIX).value == "test_ivanov_campaign1"


@pytest.mark.parametrize("raw", ["", "   ", PREFIX, f"  {PREFIX}  "])
def test_rejects_a_name_without_a_suffix(raw: str) -> None:
    with pytest.raises(InvalidCampaignName):
        CampaignName.create(raw, PREFIX)


def test_accepts_the_longest_allowed_name() -> None:
    suffix = "x" * (constants.CAMPAIGN_NAME_MAX_LENGTH - len(PREFIX))

    assert len(CampaignName.create(suffix, PREFIX).value) == constants.CAMPAIGN_NAME_MAX_LENGTH


def test_rejects_a_name_that_is_too_long() -> None:
    suffix = "x" * (constants.CAMPAIGN_NAME_MAX_LENGTH - len(PREFIX) + 1)

    with pytest.raises(InvalidCampaignName, match="at most"):
        CampaignName.create(suffix, PREFIX)
