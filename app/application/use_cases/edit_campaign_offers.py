"""Application use cases: show a campaign's offers, add an offer, remove an offer."""

from dataclasses import dataclass

from app import constants
from app.application.errors import KeitaroGatewayError
from app.application.ports import CampaignRegistry, KeitaroGateway
from app.domain.campaign import Campaign, CampaignStatus
from app.domain.errors import CampaignNotFound
from app.domain.offer_allocation import OfferAllocation


class CampaignNotEditable(Exception):
    """The campaign is not (yet) active in Keitaro, so there is nothing to edit."""


class OfferStreamNotFound(Exception):
    """The campaign has no stream that distributes traffic between offers."""


@dataclass(frozen=True, slots=True)
class OfferLine:
    """One row of the editor table."""

    offer_id: int
    name: str
    share: int


@dataclass(frozen=True, slots=True)
class OfferSummary:
    """An offer as shown in search results."""

    id: int
    name: str


@dataclass(frozen=True, slots=True)
class CampaignOffers:
    """A campaign with the offers it really has in Keitaro right now."""

    campaign: Campaign
    offers: list[OfferLine]


class EditCampaignOffers:
    """Reads and changes the offers of a campaign we created.

    Keitaro is the source of truth: every answer is built from a fresh read of its streams,
    so the numbers shown are the numbers stored there.
    """

    def __init__(self, registry: CampaignRegistry, keitaro: KeitaroGateway) -> None:
        self._registry = registry
        self._keitaro = keitaro

    def view(self, campaign_id: int) -> CampaignOffers:
        campaign, keitaro_id = self._load(campaign_id)
        stream = self._offer_stream(campaign_id, keitaro_id)
        return CampaignOffers(campaign, self._lines(stream))

    def add_offer(self, campaign_id: int, offer_id: int) -> CampaignOffers:
        """Add an offer and re-split the traffic evenly."""
        _, keitaro_id = self._load(campaign_id)
        stream = self._offer_stream(campaign_id, keitaro_id)
        allocation = OfferAllocation.of(_offer_ids(stream)).add(offer_id)
        self._keitaro.get_offer(offer_id)  # fail early if Keitaro does not know the offer
        self._store(stream, allocation)
        return self.view(campaign_id)

    def remove_offer(self, campaign_id: int, offer_id: int) -> CampaignOffers:
        """Remove an offer and re-split the traffic evenly among those that remain."""
        _, keitaro_id = self._load(campaign_id)
        stream = self._offer_stream(campaign_id, keitaro_id)
        allocation = OfferAllocation.of(_offer_ids(stream)).remove(offer_id)
        self._store(stream, allocation)
        return self.view(campaign_id)

    def replace_offers(self, campaign_id: int, offer_ids: list[int]) -> CampaignOffers:
        """Make the campaign's offers exactly this list (in this order) and split traffic evenly.

        This is the "push" of the editor: the user changes a draft first and sends it at once.
        """
        _, keitaro_id = self._load(campaign_id)
        stream = self._offer_stream(campaign_id, keitaro_id)
        allocation = OfferAllocation.of(offer_ids)
        current = set(_offer_ids(stream))
        for offer_id in allocation.offer_ids:
            if offer_id not in current:
                self._keitaro.get_offer(offer_id)  # fail early if Keitaro does not know it
        self._store(stream, allocation)
        return self.view(campaign_id)

    def search_offers(self, query: str) -> list[OfferSummary]:
        """Find offers for the autocomplete.

        A numeric query is first looked up as an exact offer ID (one cheap request); otherwise,
        or when nothing matches, offers are filtered by name substring or ID prefix (capped).
        """
        needle = query.strip().casefold()
        if needle.isdigit():
            exact = self._find_offer(int(needle))
            if exact is not None:
                return [exact]
        found: list[OfferSummary] = []
        for raw in self._keitaro.list_offers():
            offer_id = _int(raw.get("id"))
            name = _text(raw.get("name"))
            if needle in name.casefold() or str(offer_id).startswith(needle):
                found.append(OfferSummary(offer_id, name))
                if len(found) >= constants.OFFER_SEARCH_LIMIT:
                    break
        return found

    def _find_offer(self, offer_id: int) -> OfferSummary | None:
        try:
            raw = self._keitaro.get_offer(offer_id)
        except KeitaroGatewayError:
            return None
        return OfferSummary(offer_id, _text(raw.get("name")))

    def _load(self, campaign_id: int) -> tuple[Campaign, int]:
        campaign = self._registry.get(campaign_id)
        if campaign is None:
            raise CampaignNotFound(
                constants.CAMPAIGN_NOT_FOUND_TEMPLATE.format(campaign_id=campaign_id)
            )
        if campaign.status is not CampaignStatus.ACTIVE or campaign.keitaro_id is None:
            raise CampaignNotEditable(
                constants.CAMPAIGN_NOT_EDITABLE_TEMPLATE.format(campaign_id=campaign_id)
            )
        return campaign, campaign.keitaro_id

    def _offer_stream(self, campaign_id: int, keitaro_id: int) -> dict[str, object]:
        """The stream that splits traffic between offers; streams without offers are ignored."""
        candidates = [
            stream
            for stream in self._keitaro.list_streams(keitaro_id)
            if stream.get("schema") == constants.KEITARO_STREAM_SCHEMA_OFFERS
        ]
        for stream in candidates:
            if _offer_rows(stream):
                return stream
        if candidates:  # an offer stream that has no offers yet
            return candidates[0]
        raise OfferStreamNotFound(
            constants.OFFER_STREAM_NOT_FOUND_TEMPLATE.format(campaign_id=campaign_id)
        )

    def _store(self, stream: dict[str, object], allocation: OfferAllocation) -> None:
        payload = _update_payload(stream)
        payload["offers"] = [
            {
                "offer_id": item.offer_id,
                "share": item.share,
                "state": constants.KEITARO_STREAM_STATE,
            }
            for item in allocation.shares()
        ]
        stream_id = stream["id"]
        assert isinstance(stream_id, int)
        self._keitaro.update_stream(stream_id, payload)

    def _lines(self, stream: dict[str, object]) -> list[OfferLine]:
        lines: list[OfferLine] = []
        for raw in _offer_rows(stream):
            offer_id = _int(raw.get("offer_id"))
            name = _text(self._keitaro.get_offer(offer_id).get("name"))
            lines.append(OfferLine(offer_id, name, _int(raw.get("share"))))
        return lines


def _update_payload(stream: dict[str, object]) -> dict[str, object]:
    """Turn a stream read from Keitaro into a body PUT /streams/{id} accepts.

    GET returns more than PUT takes (ids, timestamps, nulls), so only the documented fields
    are copied and empty values are left out.
    """
    payload = _pick(stream, constants.KEITARO_STREAM_UPDATE_FIELDS)
    payload["filters"] = _pick_rows(stream, "filters", constants.KEITARO_STREAM_FILTER_FIELDS)
    payload["triggers"] = _pick_rows(stream, "triggers", constants.KEITARO_STREAM_TRIGGER_FIELDS)
    payload["landings"] = _pick_rows(stream, "landings", constants.KEITARO_STREAM_LANDING_FIELDS)
    return payload


def _pick(source: dict[str, object], fields: tuple[str, ...]) -> dict[str, object]:
    return {field: source[field] for field in fields if source.get(field) is not None}


def _pick_rows(
    stream: dict[str, object], key: str, fields: tuple[str, ...]
) -> list[dict[str, object]]:
    rows = stream.get(key)
    if not isinstance(rows, list):
        return []
    return [_pick(row, fields) for row in rows if isinstance(row, dict)]


def _offer_rows(stream: dict[str, object]) -> list[dict[str, object]]:
    rows = stream.get("offers")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _offer_ids(stream: dict[str, object]) -> list[int]:
    return [_int(row.get("offer_id")) for row in _offer_rows(stream)]


def _text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _int(value: object) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0
