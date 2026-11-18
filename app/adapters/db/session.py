from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app import constants
from app.config import Settings


def create_session_factory(settings: Settings) -> sessionmaker[Session]:
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_recycle=constants.DB_POOL_RECYCLE_SECONDS,
    )
    return sessionmaker(bind=engine, expire_on_commit=False)
