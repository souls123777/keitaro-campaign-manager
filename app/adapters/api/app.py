from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.orm import Session, sessionmaker

from app import constants
from app.adapters.api.routes import campaigns, health
from app.application.use_cases.create_campaign import CreateCampaign

from pathlib import Path
from fastapi.staticfiles import StaticFiles
from app.adapters.api.routes import campaign_offers
from app.application.use_cases.edit_campaign_offers import EditCampaignOffers


def create_app(
    session_factory: sessionmaker[Session],
    create_campaign_factory: Callable[[Session], CreateCampaign] | None = None,
    edit_offers_factory: Callable[[Session], EditCampaignOffers] | None = None,
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
    app.state.edit_offers_factory = edit_offers_factory
    app.include_router(campaign_offers.router)

    app.include_router(health.router)
    app.include_router(campaigns.router)

    static_dir = Path(__file__).resolve().parents[2] / constants.STATIC_DIR_NAME
    app.mount(constants.STATIC_MOUNT_PATH, StaticFiles(directory=static_dir, html=True), name="static")

    return app