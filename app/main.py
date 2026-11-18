"""Composition root: the only place where settings, adapters and the API are put together."""

from app.adapters.api.app import create_app
from app.adapters.db.session import create_session_factory
from app.config import get_settings

app = create_app(create_session_factory(get_settings()))
