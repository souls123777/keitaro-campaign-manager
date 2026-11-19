import pytest

from app.domain.errors import (
    InvalidOfferId,
    LastOfferRemoval,
    OfferAlreadyInCampaign,
    OfferNotInCampaign,
)
from app.domain.offer_allocation import OfferAllocation


def _shares(allocation: OfferAllocation) -> list[int]:
    return [item.share for item in allocation.shares()]


def test_single_offer_gets_everything() -> None:
    assert _shares(OfferAllocation.of([7])) == [100]


@pytest.mark.parametrize(
    ("count", "expected"),
    [(2, [50, 50]), (3, [34, 33, 33]), (4, [25, 25, 25, 25]), (6, [17, 17, 17, 17, 16, 16])],
)
def test_shares_are_even_and_sum_to_100(count: int, expected: list[int]) -> None:
    shares = _shares(OfferAllocation.of(list(range(1, count + 1))))
    assert shares == expected
    assert sum(shares) == 100


def test_add_appends_and_rebalances() -> None:
    allocation = OfferAllocation.of([1]).add(2).add(3)
    assert allocation.offer_ids == (1, 2, 3)
    assert _shares(allocation) == [34, 33, 33]


def test_add_does_not_mutate_original() -> None:
    original = OfferAllocation.of([1])
    original.add(2)
    assert original.offer_ids == (1,)


def test_add_duplicate_is_rejected() -> None:
    with pytest.raises(OfferAlreadyInCampaign):
        OfferAllocation.of([1, 2]).add(2)


@pytest.mark.parametrize("bad_id", [0, -5])
def test_non_positive_offer_id_is_rejected(bad_id: int) -> None:
    with pytest.raises(InvalidOfferId):
        OfferAllocation.of([1]).add(bad_id)


def test_remove_rebalances_remaining() -> None:
    allocation = OfferAllocation.of([1, 2, 3]).remove(2)
    assert allocation.offer_ids == (1, 3)
    assert _shares(allocation) == [50, 50]


def test_remove_missing_offer_is_rejected() -> None:
    with pytest.raises(OfferNotInCampaign):
        OfferAllocation.of([1, 2]).remove(9)


def test_cannot_remove_last_offer() -> None:
    with pytest.raises(LastOfferRemoval):
        OfferAllocation.of([1]).remove(1)
