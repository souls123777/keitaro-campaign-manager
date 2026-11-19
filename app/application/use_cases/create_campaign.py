"""Application use case: register a campaign and create it in Keitaro."""

import secrets
import string

from app import constants
from app.application.errors import (
    KeitaroAliasConflict,
    KeitaroGatewayError,
    KeitaroResponseError,
)
from app.application.ports import CampaignRegistry, KeitaroGateway
from app.domain.campaign import Campaign, CampaignName, GeoCodes
from app.domain.errors import CampaignAlreadyExists


class CreateCampaignError(Exception):
    """A campaign could not be created in Keitaro."""


class CreateCampaign:
    """Register a campaign as pending, then create it and its streams in Keitaro."""

    def __init__(
        self,
        registry: CampaignRegistry,
        keitaro: KeitaroGateway,
        name_prefix: str,
        domain_id: int,
        group_id: int,
        traffic_source_id: int,
    ) -> None:
        self._registry = registry
        self._keitaro = keitaro
        self._name_prefix = name_prefix
        self._domain_id = domain_id
        self._group_id = group_id
        self._traffic_source_id = traffic_source_id

    def execute(
        self,
        name: str,
        geo: str,
        offer_id: int,
    ) -> Campaign:
        """Create a campaign with two streams and return it once Keitaro is done."""
        campaign = Campaign(
            name=CampaignName.create(name, self._name_prefix),
            alias=_generate_alias(),
            geo=GeoCodes.parse(geo),
            offer_id=offer_id,
        )

        # Save as pending first so the record survives a crash in the middle of creation.
        for existing in self._registry.list_all():
            if existing.name == campaign.name:
                raise CampaignAlreadyExists(
                    constants.CAMPAIGN_ALREADY_EXISTS_TEMPLATE.format(name=campaign.name.value)
                )

        self._registry.add(campaign)

        payload = self._build_payload(campaign)

        for attempt in range(constants.KEITARO_ALIAS_MAX_ATTEMPTS):
            try:
                response = self._keitaro.create_campaign(payload)

                keitaro_id = _extract_campaign_id(response)

                self._create_streams(keitaro_id, campaign)

                campaign.mark_active(keitaro_id)
                self._registry.save(campaign)

                return campaign

            except KeitaroAliasConflict as exc:
                if attempt + 1 >= constants.KEITARO_ALIAS_MAX_ATTEMPTS:
                    campaign.mark_failed(str(exc))
                    self._registry.save(campaign)
                    raise CreateCampaignError(str(exc)) from exc

                campaign.alias = _generate_alias()
                payload = self._build_payload(campaign)

            except KeitaroGatewayError as exc:
                campaign.mark_failed(str(exc))
                self._registry.save(campaign)
                raise CreateCampaignError(str(exc)) from exc

        raise RuntimeError("Unreachable alias retry state")

    def _build_payload(self, campaign: Campaign) -> dict[str, object]:
        return {
            "name": campaign.name.value,
            "alias": campaign.alias,
            "type": constants.KEITARO_CAMPAIGN_TYPE,
            "state": constants.KEITARO_CAMPAIGN_STATE,
            "domain_id": self._domain_id,
            "group_id": self._group_id,
            "traffic_source_id": self._traffic_source_id,
        }

    def _create_streams(self, keitaro_id: int, campaign: Campaign) -> None:
        geo_codes = list(campaign.geo.codes)

        self._keitaro.create_stream(
            {
                "campaign_id": keitaro_id,
                "name": constants.KEITARO_COUNTRY_STREAM_NAME_TEMPLATE.format(
                    geo=constants.GEO_SEPARATOR.join(geo_codes)
                ),
                "type": constants.KEITARO_STREAM_TYPE_REGULAR,
                "position": constants.KEITARO_COUNTRY_STREAM_POSITION,
                "state": constants.KEITARO_STREAM_STATE,
                "schema": constants.KEITARO_STREAM_SCHEMA_REDIRECT,
                "action_type": constants.KEITARO_STREAM_ACTION_HTTP,
                "action_payload": constants.KEITARO_REDIRECT_URL,
                "filters": [
                    {
                        "name": constants.KEITARO_FILTER_COUNTRY,
                        "mode": constants.KEITARO_FILTER_MODE_ACCEPT,
                        "payload": geo_codes,
                    }
                ],
            }
        )
        self._keitaro.create_stream(
            {
                "campaign_id": keitaro_id,
                "name": constants.KEITARO_OFFER_STREAM_NAME,
                "type": constants.KEITARO_STREAM_TYPE_DEFAULT,
                "position": constants.KEITARO_OFFER_STREAM_POSITION,
                "state": constants.KEITARO_STREAM_STATE,
                "schema": constants.KEITARO_STREAM_SCHEMA_OFFERS,
                "action_type": constants.KEITARO_STREAM_ACTION_HTTP,
                "action_payload": constants.KEITARO_EMPTY_ACTION_PAYLOAD,
                "offers": [
                    {
                        "offer_id": campaign.offer_id,
                        "share": constants.KEITARO_FULL_SHARE,
                        "state": constants.KEITARO_STREAM_STATE,
                    }
                ],
            }
        )


def _generate_alias() -> str:
    alphabet = string.ascii_letters + string.digits

    return "".join(secrets.choice(alphabet) for _ in range(constants.CAMPAIGN_ALIAS_LENGTH))


def _extract_campaign_id(response: dict[str, object]) -> int:
    raw_id = response.get("id")

    if isinstance(raw_id, bool) or not isinstance(raw_id, int) or raw_id <= 0:
        raise KeitaroResponseError("Keitaro response does not contain a valid positive campaign id")

    return raw_id
