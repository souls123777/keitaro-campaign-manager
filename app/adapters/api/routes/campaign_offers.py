"""HTTP API of the offer editor and the campaign list."""

from collections.abc import Callable
from typing import Annotated, NoReturn, TypeVar

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import constants
from app.adapters.api.dependencies import get_session
from app.adapters.db.repository import SqlAlchemyCampaignRegistry
from app.application.errors import KeitaroGatewayError
from app.application.use_cases.edit_campaign_offers import (
    CampaignNotEditable,
    CampaignOffers,
    EditCampaignOffers,
    OfferStreamNotFound,
)
from app.domain.campaign import Campaign
from app.domain.errors import (
    CampaignNotFound,
    InvalidOfferId,
    OfferAlreadyInCampaign,
    OfferNotInCampaign,
)

router = APIRouter()

T = TypeVar("T")

_STATUS_BY_ERROR: dict[type[Exception], int] = {
    CampaignNotFound: status.HTTP_404_NOT_FOUND,
    OfferNotInCampaign: status.HTTP_404_NOT_FOUND,
    OfferAlreadyInCampaign: status.HTTP_409_CONFLICT,
    CampaignNotEditable: status.HTTP_409_CONFLICT,
    OfferStreamNotFound: status.HTTP_409_CONFLICT,
    InvalidOfferId: status.HTTP_422_UNPROCESSABLE_CONTENT,
    KeitaroGatewayError: status.HTTP_502_BAD_GATEWAY,
}


class CampaignOut(BaseModel):
    id: int
    name: str
    alias: str
    geo: list[str]
    status: str
    keitaro_id: int | None


class OfferLineOut(BaseModel):
    offer_id: int
    name: str
    share: int


class CampaignOffersOut(BaseModel):
    campaign: CampaignOut
    offers: list[OfferLineOut]


class OfferSummaryOut(BaseModel):
    id: int
    name: str


class AddOfferIn(BaseModel):
    offer_id: int


class ReplaceOffersIn(BaseModel):
    offer_ids: list[int]


def get_editor(
    request: Request, session: Annotated[Session, Depends(get_session)]
) -> EditCampaignOffers:
    factory: Callable[[Session], EditCampaignOffers] | None = request.app.state.edit_offers_factory
    if factory is None:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, constants.EDITOR_NOT_CONFIGURED_MESSAGE
        )
    return factory(session)


Editor = Annotated[EditCampaignOffers, Depends(get_editor)]


def _fail(error: Exception) -> NoReturn:
    for error_type, code in _STATUS_BY_ERROR.items():
        if isinstance(error, error_type):
            raise HTTPException(code, str(error)) from error
    raise error


def _run(action: Callable[[], T]) -> T:
    try:
        return action()
    except tuple(_STATUS_BY_ERROR) as error:
        _fail(error)


def _campaign_out(campaign: Campaign) -> CampaignOut:
    assert campaign.id is not None
    return CampaignOut(
        id=campaign.id,
        name=campaign.name.value,
        alias=campaign.alias,
        geo=list(campaign.geo.codes),
        status=campaign.status.value,
        keitaro_id=campaign.keitaro_id,
    )


def _offers_out(result: CampaignOffers) -> CampaignOffersOut:
    return CampaignOffersOut(
        campaign=_campaign_out(result.campaign),
        offers=[
            OfferLineOut(offer_id=o.offer_id, name=o.name, share=o.share) for o in result.offers
        ],
    )


@router.get(constants.CAMPAIGNS_LIST_PATH, response_model=list[CampaignOut])
def list_campaigns(session: Annotated[Session, Depends(get_session)]) -> list[CampaignOut]:
    """Campaigns created through this service, newest first."""
    return [_campaign_out(item) for item in SqlAlchemyCampaignRegistry(session).list_all()]


@router.get(constants.CAMPAIGN_OFFERS_PATH, response_model=CampaignOffersOut)
def get_campaign_offers(campaign_id: int, editor: Editor) -> CampaignOffersOut:
    """Offers of a campaign with their real shares, read from Keitaro."""
    return _offers_out(_run(lambda: editor.view(campaign_id)))


@router.post(constants.CAMPAIGN_OFFERS_PATH, response_model=CampaignOffersOut)
def add_campaign_offer(campaign_id: int, body: AddOfferIn, editor: Editor) -> CampaignOffersOut:
    """Add an offer; the traffic is re-split evenly."""
    return _offers_out(_run(lambda: editor.add_offer(campaign_id, body.offer_id)))


@router.put(constants.CAMPAIGN_OFFERS_PATH, response_model=CampaignOffersOut)
def replace_campaign_offers(
    campaign_id: int, body: ReplaceOffersIn, editor: Editor
) -> CampaignOffersOut:
    """Push a whole draft: the campaign gets exactly these offers, traffic split evenly."""
    return _offers_out(_run(lambda: editor.replace_offers(campaign_id, body.offer_ids)))


@router.delete(constants.CAMPAIGN_OFFER_PATH, response_model=CampaignOffersOut)
def remove_campaign_offer(campaign_id: int, offer_id: int, editor: Editor) -> CampaignOffersOut:
    """Remove an offer; the traffic is re-split evenly."""
    return _offers_out(_run(lambda: editor.remove_offer(campaign_id, offer_id)))


@router.get(constants.OFFERS_SEARCH_PATH, response_model=list[OfferSummaryOut])
def search_offers(
    editor: Editor, query: Annotated[str, Query(min_length=1)]
) -> list[OfferSummaryOut]:
    """Search Keitaro offers by name or ID for the autocomplete."""
    found = _run(lambda: editor.search_offers(query))
    return [OfferSummaryOut(id=item.id, name=item.name) for item in found]
