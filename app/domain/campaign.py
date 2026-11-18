"""Campaign model: validated value objects and the creation lifecycle."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Self

from app import constants
from app.domain.errors import (
    InvalidCampaignName,
    InvalidGeoCodes,
    InvalidOfferId,
    InvalidStatusTransition,
)


class CampaignStatus(StrEnum):
    """Where a campaign stands while we create it in Keitaro."""

    PENDING = "pending"
    ACTIVE = "active"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class CampaignName:
    """A campaign name that always carries the configured prefix."""

    value: str

    @classmethod
    def create(cls, raw: str, prefix: str) -> Self:
        suffix = raw.strip().removeprefix(prefix)
        if not suffix:
            raise InvalidCampaignName(constants.EMPTY_CAMPAIGN_NAME_MESSAGE)

        name = prefix + suffix
        if len(name) > constants.CAMPAIGN_NAME_MAX_LENGTH:
            raise InvalidCampaignName(
                constants.CAMPAIGN_NAME_TOO_LONG_TEMPLATE.format(
                    limit=constants.CAMPAIGN_NAME_MAX_LENGTH, actual=len(name)
                )
            )
        return cls(name)


@dataclass(frozen=True, slots=True)
class GeoCodes:
    """One or more two-letter country codes, upper-cased and without duplicates."""

    codes: tuple[str, ...]

    @classmethod
    def parse(cls, raw: str) -> Self:
        candidates = [part.strip().upper() for part in raw.split(constants.GEO_SEPARATOR)]
        codes = [code for code in dict.fromkeys(candidates) if code]
        if not codes:
            raise InvalidGeoCodes(constants.EMPTY_GEO_MESSAGE)

        invalid = [code for code in codes if not _is_country_code(code)]
        if invalid:
            raise InvalidGeoCodes(
                constants.INVALID_GEO_TEMPLATE.format(
                    codes=constants.GEO_DISPLAY_SEPARATOR.join(invalid)
                )
            )
        return cls(tuple(codes))


def _is_country_code(code: str) -> bool:
    return len(code) == constants.GEO_CODE_LENGTH and code.isascii() and code.isalpha()


def _utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(slots=True)
class Campaign:
    """A campaign we create in Keitaro. We keep our own record of it and of its progress."""

    name: CampaignName
    alias: str
    geo: GeoCodes
    offer_id: int
    status: CampaignStatus = CampaignStatus.PENDING
    keitaro_id: int | None = None
    error: str | None = None
    created_at: datetime = field(default_factory=_utc_now)
    id: int | None = None

    def __post_init__(self) -> None:
        if self.offer_id <= 0:
            raise InvalidOfferId(constants.INVALID_OFFER_ID_TEMPLATE.format(offer_id=self.offer_id))

    def mark_active(self, keitaro_id: int) -> None:
        self._leave_pending(CampaignStatus.ACTIVE)
        self.keitaro_id = keitaro_id
        self.error = None

    def mark_failed(self, reason: str) -> None:
        self._leave_pending(CampaignStatus.FAILED)
        self.error = reason

    def _leave_pending(self, target: CampaignStatus) -> None:
        if self.status is not CampaignStatus.PENDING:
            raise InvalidStatusTransition(
                constants.INVALID_TRANSITION_TEMPLATE.format(
                    current=self.status.value, target=target.value
                )
            )
        self.status = target
