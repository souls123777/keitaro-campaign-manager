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
