from fastapi import FastAPI
from sqlalchemy.orm import Session, sessionmaker

from app import constants
from app.adapters.api.routes import health


def create_app(session_factory: sessionmaker[Session]) -> FastAPI:
    app = FastAPI(title=constants.APP_TITLE, version=constants.APP_VERSION)
    app.state.session_factory = session_factory
    app.include_router(health.router)
    return app
