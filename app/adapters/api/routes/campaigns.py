"""HTTP endpoints for campaign creation."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app import constants
from app.adapters.api.dependencies import get_create_campaign
from app.application.use_cases.create_campaign import (
    CreateCampaign,
    CreateCampaignError,
)
from app.domain.campaign import Campaign
from app.domain.errors import DomainError

router = APIRouter()


class CreateCampaignRequest(BaseModel):
    """User input for a new campaign."""

    name: str = Field(
        min_length=1,
        max_length=constants.CAMPAIGN_NAME_MAX_LENGTH,
    )
    geo: str = Field(min_length=1)
    offer_id: int = Field(gt=0)


class CampaignResponse(BaseModel):
    """A stored campaign as returned to the client."""

    id: int
    keitaro_id: int | None
    name: str
    alias: str
    geo: list[str]
    offer_id: int
    status: str
    error: str | None

    @classmethod
    def from_entity(cls, campaign: Campaign) -> "CampaignResponse":
        """Build the response from a stored campaign."""
        if campaign.id is None:
            raise RuntimeError("Stored campaign must have a local id")

        return cls(
            id=campaign.id,
            keitaro_id=campaign.keitaro_id,
            name=campaign.name.value,
            alias=campaign.alias,
            geo=list(campaign.geo.codes),
            offer_id=campaign.offer_id,
            status=campaign.status.value,
            error=campaign.error,
        )


@router.post(
    constants.CAMPAIGNS_PATH,
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_campaign(
    payload: CreateCampaignRequest,
    use_case: Annotated[
        CreateCampaign,
        Depends(get_create_campaign),
    ],
) -> CampaignResponse:
    """Create a campaign in Keitaro and store it in our registry."""
    try:
        campaign = use_case.execute(
            name=payload.name,
            geo=payload.geo,
            offer_id=payload.offer_id,
        )

    except DomainError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    except CreateCampaignError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return CampaignResponse.from_entity(campaign)
