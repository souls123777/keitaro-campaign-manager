"""Offers of a campaign and how the traffic is split between them."""

from dataclasses import dataclass
from typing import Self

from app import constants
from app.domain.errors import (
    InvalidOfferId,
    OfferAlreadyInCampaign,
    OfferNotInCampaign,
)


@dataclass(frozen=True, slots=True)
class OfferShare:
    """The part of the traffic (in percent) that goes to one offer."""

    offer_id: int
    share: int


@dataclass(frozen=True, slots=True)
class OfferAllocation:
    """Ordered offers of a campaign; the traffic is always split evenly and sums to 100.

    The object is immutable: `add` and `remove` return a new allocation.
    """

    offer_ids: tuple[int, ...]

    @classmethod
    def of(cls, offer_ids: list[int]) -> Self:
        for offer_id in offer_ids:
            _ensure_valid(offer_id)
        return cls(tuple(dict.fromkeys(offer_ids)))

    def add(self, offer_id: int) -> Self:
        """Append an offer; fails if it is invalid or already there."""
        _ensure_valid(offer_id)
        if offer_id in self.offer_ids:
            raise OfferAlreadyInCampaign(
                constants.OFFER_ALREADY_IN_CAMPAIGN_TEMPLATE.format(offer_id=offer_id)
            )
        return type(self)((*self.offer_ids, offer_id))

    def remove(self, offer_id: int) -> Self:
        """Drop an offer; fails if it is not there. Removing the last offer is allowed."""
        if offer_id not in self.offer_ids:
            raise OfferNotInCampaign(
                constants.OFFER_NOT_IN_CAMPAIGN_TEMPLATE.format(offer_id=offer_id)
            )
        return type(self)(tuple(item for item in self.offer_ids if item != offer_id))

    def shares(self) -> list[OfferShare]:
        """Split 100% evenly; the remainder goes one point at a time to the first offers."""
        if not self.offer_ids:
            return []
        base, remainder = divmod(constants.FULL_SHARE, len(self.offer_ids))
        return [
            OfferShare(offer_id, base + (1 if index < remainder else 0))
            for index, offer_id in enumerate(self.offer_ids)
        ]


def _ensure_valid(offer_id: int) -> None:
    if offer_id <= 0:
        raise InvalidOfferId(constants.INVALID_OFFER_ID_TEMPLATE.format(offer_id=offer_id))
