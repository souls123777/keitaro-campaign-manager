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

# --- Offer allocation ---
FULL_SHARE = 100
OFFER_ALREADY_IN_CAMPAIGN_TEMPLATE = "Offer {offer_id} is already in this campaign."
OFFER_NOT_IN_CAMPAIGN_TEMPLATE = "Offer {offer_id} is not in this campaign."
LAST_OFFER_REMOVAL_MESSAGE = "A campaign must keep at least one offer."

# --- Editor ---

# Fields Keitaro accepts in PUT /streams/{id}; anything else from GET is dropped.
KEITARO_STREAM_UPDATE_FIELDS = (
    "campaign_id", "type", "name", "position", "weight", "action_options",
    "comments", "state", "action_type", "action_payload", "schema",
    "collect_clicks", "filter_or",
)
KEITARO_STREAM_FILTER_FIELDS = ("id", "name", "mode", "payload")
KEITARO_STREAM_TRIGGER_FIELDS = (
    "id", "stream_id", "condition", "target", "selected_page", "pattern",
    "action", "interval", "alternative_urls", "grab_from_page", "av_settings",
    "reverse", "scan_page",
)
KEITARO_STREAM_LANDING_FIELDS = ("landing_id", "share", "state")
OFFER_SEARCH_LIMIT = 20
CAMPAIGN_NOT_EDITABLE_TEMPLATE = (
    "Campaign {campaign_id} is not active in Keitaro and cannot be edited."
)
OFFER_STREAM_NOT_FOUND_TEMPLATE = "Campaign {campaign_id} has no stream with offers."
CAMPAIGNS_LIST_PATH = "/campaigns"
CAMPAIGN_OFFERS_PATH = "/campaigns/{campaign_id}/offers"
CAMPAIGN_OFFER_PATH = "/campaigns/{campaign_id}/offers/{offer_id}"
OFFERS_SEARCH_PATH = "/offers"
STATIC_DIR_NAME = "static"
STATIC_MOUNT_PATH = "/"
EDITOR_NOT_CONFIGURED_MESSAGE = "The offer editor is not configured."
KEITARO_STREAMS_OF_CAMPAIGN_PATH = "/campaigns/{campaign_id}/streams"
KEITARO_STREAM_PATH = "/streams/{stream_id}"
KEITARO_OFFERS_PATH = "/offers"
KEITARO_OFFER_PATH = "/offers/{offer_id}"
KEITARO_CAMPAIGN_PATH = "/campaigns/{campaign_id}"

# --- HTTP --------------------------------------------------------------------
HTTP_ALIAS_CONFLICT_STATUS = 409
HTTP_GET = "GET"
HTTP_POST = "POST"
HTTP_PUT = "PUT"
HTTP_DELETE = "DELETE"
