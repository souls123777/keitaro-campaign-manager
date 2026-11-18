"""Every number, string and setting name used by the application, grouped by topic."""

# --- Application -------------------------------------------------------------
APP_TITLE = "Keitaro Campaign Manager"
APP_VERSION = "0.1.0"

# --- Configuration -----------------------------------------------------------
ENV_FILE = ".env"
DEFAULT_DB_HOST = "localhost"
DEFAULT_DB_PORT = 3306

# --- Database ----------------------------------------------------------------
DB_DRIVER = "mysql+pymysql"
DB_CHARSET = "utf8mb4"
DB_POOL_RECYCLE_SECONDS = 3600
DB_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
CAMPAIGNS_TABLE = "campaigns"
HEALTH_QUERY = "SELECT 1"

# --- Campaign ----------------------------------------------------------------
CAMPAIGN_NAME_MAX_LENGTH = 255
CAMPAIGN_ALIAS_MAX_LENGTH = 32
CAMPAIGN_STATUS_MAX_LENGTH = 16
GEO_CODE_LENGTH = 2
GEO_SEPARATOR = ","
GEO_DISPLAY_SEPARATOR = ", "

# --- API ---------------------------------------------------------------------
HEALTH_PATH = "/health"
HEALTH_STATUS_OK = "ok"
HEALTH_STATUS_UNAVAILABLE = "unavailable"

# --- Error messages ----------------------------------------------------------
EMPTY_CAMPAIGN_NAME_MESSAGE = "Campaign name must not be empty."
CAMPAIGN_NAME_TOO_LONG_TEMPLATE = "Campaign name must be at most {limit} characters, got {actual}."
EMPTY_GEO_MESSAGE = "At least one country code is required."
INVALID_GEO_TEMPLATE = (
    "Invalid country codes: {codes}. Expected two-letter codes such as MX, AU, RO."
)
INVALID_OFFER_ID_TEMPLATE = "Offer id must be positive, got {offer_id}."
INVALID_TRANSITION_TEMPLATE = "Cannot move a campaign from {current} to {target}."
CAMPAIGN_NOT_FOUND_TEMPLATE = "Campaign {campaign_id} does not exist."

# --- Keitaro -----------------------------------------------------------------
KEITARO_API_PREFIX = "/admin_api/v1"
KEITARO_CAMPAIGN_TYPE = "position"
KEITARO_CAMPAIGN_STATE = "active"
KEITARO_ALIAS_MAX_ATTEMPTS = 3
CAMPAIGN_ALIAS_LENGTH = 8
KEITARO_COUNTRY_STREAM_NAME_TEMPLATE = "Google ({geo})"
KEITARO_OFFER_STREAM_NAME = "Offers"
KEITARO_REDIRECT_URL = "https://google.com"

# --- Keitaro streams-----------------------------------------------------------
KEITARO_STREAMS_PATH = "/streams"
KEITARO_CAMPAIGN_PATH_TEMPLATE = "/campaigns/{campaign_id}"
KEITARO_STREAM_TYPE_REGULAR = "regular"
KEITARO_STREAM_TYPE_DEFAULT = "default"
KEITARO_STREAM_STATE = "active"
KEITARO_STREAM_SCHEMA_REDIRECT = "redirect"
KEITARO_STREAM_SCHEMA_OFFERS = "landings"
KEITARO_STREAM_ACTION_HTTP = "http"
KEITARO_FILTER_COUNTRY = "country"
KEITARO_FILTER_MODE_ACCEPT = "accept"
KEITARO_FULL_SHARE = 100
KEITARO_COUNTRY_STREAM_POSITION = 1
KEITARO_OFFER_STREAM_POSITION = 2
KEITARO_EMPTY_ACTION_PAYLOAD = ""

# --- Campaign API ------------------------------------------------------------
CAMPAIGNS_PATH = "/campaigns"
