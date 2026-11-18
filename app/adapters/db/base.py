from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from app import constants


class Base(DeclarativeBase):
    # Explicit constraint names keep Alembic migrations stable across databases.
    metadata = MetaData(naming_convention=constants.DB_NAMING_CONVENTION)
