from datetime import UTC

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import constants
from app.adapters.db.models import CampaignRecord
from app.domain.campaign import Campaign, CampaignName, CampaignStatus, GeoCodes
from app.domain.errors import CampaignNotFound


class SqlAlchemyCampaignRegistry:
    """CampaignRegistry backed by the `campaigns` table.

    Every method commits at once: a campaign must be stored as `pending` before Keitaro is
    called, and that record has to survive a crash in the middle of the creation.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, campaign: Campaign) -> Campaign:
        record = CampaignRecord()
        _copy_to_record(campaign, record)
        self._session.add(record)
        self._session.flush()
        campaign.id = record.id
        self._session.commit()
        return campaign

    def get(self, campaign_id: int) -> Campaign | None:
        record = self._session.get(CampaignRecord, campaign_id)
        return _to_entity(record) if record is not None else None

    def save(self, campaign: Campaign) -> None:
        record = self._session.get(CampaignRecord, campaign.id) if campaign.id is not None else None
        if record is None:
            raise CampaignNotFound(
                constants.CAMPAIGN_NOT_FOUND_TEMPLATE.format(campaign_id=campaign.id)
            )
        _copy_to_record(campaign, record)
        self._session.commit()

    def list_all(self) -> list[Campaign]:
        records = self._session.scalars(select(CampaignRecord).order_by(CampaignRecord.id.desc()))
        return [_to_entity(record) for record in records]


def _copy_to_record(campaign: Campaign, record: CampaignRecord) -> None:
    record.keitaro_id = campaign.keitaro_id
    record.alias = campaign.alias
    record.name = campaign.name.value
    record.geo = list(campaign.geo.codes)
    record.offer_id = campaign.offer_id
    record.status = campaign.status.value
    record.error = campaign.error
    record.created_at = campaign.created_at.astimezone(UTC).replace(tzinfo=None)


def _to_entity(record: CampaignRecord) -> Campaign:
    return Campaign(
        id=record.id,
        name=CampaignName(record.name),
        alias=record.alias,
        geo=GeoCodes(tuple(record.geo)),
        offer_id=record.offer_id,
        status=CampaignStatus(record.status),
        keitaro_id=record.keitaro_id,
        error=record.error,
        created_at=record.created_at.replace(tzinfo=UTC),
    )
