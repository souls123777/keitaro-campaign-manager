"""Composition root: the only place where settings, adapters and the API are put together."""

from sqlalchemy.orm import Session

from app.adapters.api.app import create_app
from app.adapters.db.repository import SqlAlchemyCampaignRegistry
from app.adapters.db.session import create_session_factory
from app.adapters.keitaro.client import KeitaroHttpClient
from app.adapters.keitaro.gateway import KeitaroHttpGateway
from app.application.use_cases.create_campaign import CreateCampaign
from app.application.use_cases.edit_campaign_offers import EditCampaignOffers
from app.config import get_settings


settings = get_settings()

session_factory = create_session_factory(settings)

keitaro_client = KeitaroHttpClient(
    base_url=settings.keitaro_url,
    api_key=settings.keitaro_api_key.get_secret_value(),
)

keitaro_gateway = KeitaroHttpGateway(keitaro_client)


def create_campaign_factory(session: Session) -> CreateCampaign:
    return CreateCampaign(
        registry=SqlAlchemyCampaignRegistry(session),
        keitaro=keitaro_gateway,
        name_prefix=settings.campaign_name_prefix,
        domain_id=settings.keitaro_domain_id,
        group_id=settings.keitaro_group_id,
        traffic_source_id=settings.keitaro_traffic_source_id,
    )



app = create_app(
    session_factory=session_factory,
    create_campaign_factory=create_campaign_factory,
    edit_offers_factory=lambda session: EditCampaignOffers(SqlAlchemyCampaignRegistry(session), keitaro_gateway),
    close_keitaro=keitaro_gateway.close,
)
