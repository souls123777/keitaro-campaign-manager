"""FastAPI dependencies shared by the routers."""

from collections.abc import Callable, Iterator
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session, sessionmaker

from app.application.use_cases.create_campaign import CreateCampaign


def get_session(request: Request) -> Iterator[Session]:
    session_factory: sessionmaker[Session] = request.app.state.session_factory

    with session_factory() as session:
        yield session


def get_create_campaign(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
) -> CreateCampaign:
    factory: Callable[[Session], CreateCampaign] | None = getattr(
        request.app.state,
        "create_campaign_factory",
        None,
    )

    if factory is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Keitaro integration is not configured",
        )

    return factory(session)
