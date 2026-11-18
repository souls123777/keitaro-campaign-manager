from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import constants
from app.adapters.api.dependencies import get_session

router = APIRouter()


class HealthResponse(BaseModel):
    status: str


@router.get(constants.HEALTH_PATH, response_model=HealthResponse)
def health(response: Response, session: Annotated[Session, Depends(get_session)]) -> HealthResponse:
    """Readiness check: answers 200 only when the database is reachable."""
    try:
        session.execute(text(constants.HEALTH_QUERY))
    except SQLAlchemyError:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthResponse(status=constants.HEALTH_STATUS_UNAVAILABLE)
    return HealthResponse(status=constants.HEALTH_STATUS_OK)
