from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.orm import Session, sessionmaker

from app import constants
from app.adapters.api.routes import campaigns, health
from app.application.use_cases.create_campaign import CreateCampaign


def create_app(
    session_factory: sessionmaker[Session],
    create_campaign_factory: Callable[[Session], CreateCampaign] | None = None,
    close_keitaro: Callable[[], None] | None = None,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            if close_keitaro is not None:
                close_keitaro()

    app = FastAPI(
        title=constants.APP_TITLE,
        version=constants.APP_VERSION,
        lifespan=lifespan,
    )

    app.state.session_factory = session_factory
    app.state.create_campaign_factory = create_campaign_factory

    app.include_router(health.router)
    app.include_router(campaigns.router)

    return app