"""QCK SDK type definitions.

Contains :class:`~typing.TypedDict` definitions for every request parameter
object and response shape used by the SDK. These types enable static type
checking and IDE autocompletion without adding any runtime overhead.

The types are organised into sections matching the API resource they
belong to: Links, Analytics, Domains, Webhooks, Journey, and Conversions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypedDict


# --------------------------------------------------------------------------
# Generic response wrappers
# --------------------------------------------------------------------------

class ErrorDetail(TypedDict, total=False):
    """Machine-readable error detail returned inside API error responses.

    Attributes:
        code: Error code string (e.g. ``"VALIDATION_ERROR"``).
        message: Human-readable error description.
    """

    code: str
    message: str


class ApiResponse(TypedDict, total=False):
    """Standard API response envelope.

    All QCK API endpoints return this shape. The SDK unwraps it
    automatically, so callers receive the ``data`` field directly.

    Attributes:
        success: Whether the request succeeded.
        data: Response payload (type varies by endpoint).
        error: Present only when ``success`` is ``False``.
    """

    success: bool
    data: Any
    error: ErrorDetail


class PaginatedResponse(TypedDict):
    """Paginated list response returned by endpoints that support paging.

    Attributes:
        data: List of items for the current page.
        total: Total number of items across all pages.
        page: Current page number (1-based).
        limit: Maximum items per page.
    """

    data: List[Any]
    total: int
    page: int
    limit: int


# --------------------------------------------------------------------------
# Links
# --------------------------------------------------------------------------

class LinkMetadata(TypedDict, total=False):
    """Metadata scraped or configured for a short link's destination.

    Attributes:
        title: Page title from the destination URL.
        description: Meta description from the destination URL.
        og_image: Open Graph image URL.
        domain: Domain name of the destination URL.
        is_safe: Whether the destination passed safety checks.
        tags: User-assigned tags for organisation.
    """

    title: str
    description: str
    og_image: str
    domain: str
    is_safe: bool
    tags: List[str]


class Link(TypedDict, total=False):
    """A short link returned by the API.

    Attributes:
        id: Unique link identifier.
        link_id: The generated or custom alias (e.g. ``"abc123"``).
        original_url: The destination URL the short link redirects to.
        short_url: Fully qualified short URL (e.g. ``"https://qck.sh/abc123"``).
        title: User-supplied or scraped page title.
        description: User-supplied or scraped meta description.
        expires_at: ISO-8601 expiration timestamp, or absent if none.
        created_at: ISO-8601 creation timestamp.
        updated_at: ISO-8601 last-modified timestamp.
        is_active: Whether the link is currently active and redirecting.
        tags: User-assigned tags for organisation and filtering.
        is_password_protected: Whether the link requires a password to access.
        metadata: Scraped metadata from the destination URL.
        total_clicks: Lifetime click count.
        unique_visitors: Lifetime unique visitor count.
        bot_clicks: Lifetime bot/crawler click count.
        last_accessed_at: ISO-8601 timestamp of the most recent click.
        domain_id: ID of the custom domain this link uses.
        domain_name: Custom domain name (e.g. ``"links.example.com"``).
    """

    id: str
    link_id: str
    original_url: str
    short_url: str
    title: str
    description: str
    expires_at: str
    created_at: str
    updated_at: str
    is_active: bool
    tags: List[str]
    is_password_protected: bool
    metadata: LinkMetadata
    total_clicks: int
    unique_visitors: int
    bot_clicks: int
    last_accessed_at: str
    domain_id: str
    domain_name: str


class CreateLinkParams(TypedDict, total=False):
    """Parameters for creating a new short link.

    Only ``url`` is required; all other fields are optional.

    Attributes:
        url: Destination URL to shorten (required).
        custom_alias: Custom short code (3+ characters, Basic tier+).
        title: Override the scraped page title.
        description: Override the scraped meta description.
        og_image: Override the scraped Open Graph image URL.
        tags: Tags for organising links.
        expires_at: ISO-8601 expiration timestamp.
        is_password_protected: Enable password protection.
        password: Password required to access the link.
        utm_source: UTM source parameter appended to the destination.
        utm_medium: UTM medium parameter.
        utm_campaign: UTM campaign parameter.
        utm_term: UTM term parameter.
        utm_content: UTM content parameter.
        domain_id: ID of the custom domain to use for the short URL.
    """

    url: str
    custom_alias: str
    title: str
    description: str
    og_image: str
    tags: List[str]
    expires_at: str
    is_password_protected: bool
    password: str
    utm_source: str
    utm_medium: str
    utm_campaign: str
    utm_term: str
    utm_content: str
    domain_id: str


class UpdateLinkParams(TypedDict, total=False):
    """Parameters for updating an existing short link.

    Only include the fields you want to change.

    Attributes:
        url: New destination URL.
        custom_alias: New custom short code.
        title: New title.
        description: New description.
        og_image: New Open Graph image URL.
        expires_at: New expiration timestamp, or ``None`` to remove.
        is_active: Enable or disable the link.
        tags: Replace the link's tags with this list.
        is_password_protected: Enable or disable password protection.
        password: New password (only when enabling protection).
    """

    url: str
    custom_alias: str
    title: str
    description: str
    og_image: str
    expires_at: Optional[str]
    is_active: bool
    tags: List[str]
    is_password_protected: bool
    password: str


class ListLinksParams(TypedDict, total=False):
    """Query parameters for listing links with filtering and pagination.

    Attributes:
        page: Page number (1-based). Defaults to 1.
        per_page: Items per page. Defaults to 20.
        search: Free-text search across URL, title, and tags.
        tags: Filter to links that have all of these tags.
        is_active: Filter by active/inactive status.
        has_password: Filter by password-protected status.
        domain: Filter by custom domain name.
        domain_id: Filter by custom domain ID.
        created_after: ISO-8601 lower bound on creation date.
        created_before: ISO-8601 upper bound on creation date.
        last_active_after: ISO-8601 lower bound on last click date.
        sort_by: Field to sort by (e.g. ``"created_at"``,
            ``"total_clicks"``).
        sort_order: Sort direction: ``"asc"`` or ``"desc"``.
    """

    page: int
    per_page: int
    search: str
    tags: List[str]
    is_active: bool
    has_password: bool
    domain: str
    domain_id: str
    created_after: str
    created_before: str
    last_active_after: str
    sort_by: str
    sort_order: Literal["asc", "desc"]


class BulkCreateParams(TypedDict):
    """Parameters for bulk-creating multiple links in a single request.

    Attributes:
        links: List of link creation parameter objects.
    """

    links: List[CreateLinkParams]


class LinkStats(TypedDict):
    """Click statistics for a single link.

    Attributes:
        short_code: The link's short code (e.g. ``"abc123"``).
        original_url: The destination URL.
        total_clicks: Total click count.
        unique_visitors: Unique visitor count.
        bot_clicks: Bot/crawler click count.
        human_clicks: Total clicks minus bot clicks.
        created_at: ISO-8601 creation timestamp.
        last_accessed_at: ISO-8601 timestamp of most recent click,
            or ``None`` if never clicked.
        is_active: Whether the link is currently active.
        days_active: Days since the link was created.
        average_clicks_per_day: Average clicks per day since creation.
        conversion_rate: Ratio of unique visitors to total clicks (0-1).
    """

    short_code: str
    original_url: str
    total_clicks: int
    unique_visitors: int
    bot_clicks: int
    human_clicks: int
    created_at: str
    last_accessed_at: Optional[str]
    is_active: bool
    days_active: int
    average_clicks_per_day: float
    conversion_rate: float


# --------------------------------------------------------------------------
# Analytics
# --------------------------------------------------------------------------

class AnalyticsSummaryParams(TypedDict, total=False):
    """Query parameters for the analytics summary endpoint.

    Specify a date range with either ``days`` (rolling window) or an
    explicit ``start_date``/``end_date`` pair.

    Attributes:
        start_date: ISO-8601 start date (inclusive).
        end_date: ISO-8601 end date (inclusive).
        days: Rolling window in days (e.g. 30 for the last 30 days).
        bot_filter: Traffic filter: ``"real"`` (humans only),
            ``"bot"`` (crawlers only), or ``"all"``.
        domain_name: Restrict results to a specific custom domain.
    """

    start_date: str
    end_date: str
    days: int
    bot_filter: Literal["real", "bot", "all"]
    domain_name: str


class AnalyticsSummary(TypedDict):
    """Aggregated analytics summary for an account or domain.

    Attributes:
        total_clicks: Total click count in the period.
        unique_visitors: Unique visitor count in the period.
        total_links: Number of links that received clicks.
        last_click_at: ISO-8601 timestamp of the most recent click,
            or ``None`` if no clicks occurred.
        today_clicks: Click count for the current calendar day.
        yesterday_clicks: Click count for yesterday.
        active_links: Number of currently active links.
        total_links_count: Total number of links in the account.
    """

    total_clicks: int
    unique_visitors: int
    total_links: int
    last_click_at: Optional[str]
    today_clicks: int
    yesterday_clicks: int
    active_links: int
    total_links_count: int


class TimeseriesParams(TypedDict, total=False):
    """Query parameters for the click timeseries endpoint.

    Attributes:
        start_date: ISO-8601 start date (inclusive).
        end_date: ISO-8601 end date (inclusive).
        days: Rolling window in days.
        bot_filter: Traffic filter: ``"real"``, ``"bot"``, or ``"all"``.
        domain_name: Restrict results to a specific custom domain.
    """

    start_date: str
    end_date: str
    days: int
    bot_filter: Literal["real", "bot", "all"]
    domain_name: str


class TimeseriesPoint(TypedDict):
    """A single data point in a click timeseries.

    Attributes:
        timestamp: ISO-8601 timestamp for this bucket.
        clicks: Total clicks in the bucket.
        unique_visitors: Unique visitors in the bucket.
    """

    timestamp: str
    clicks: int
    unique_visitors: int


class GeoAnalyticsParams(TypedDict, total=False):
    """Query parameters for geographic analytics.

    Attributes:
        days: Rolling window in days.
        start_date: ISO-8601 start date (inclusive).
        end_date: ISO-8601 end date (inclusive).
        bot_filter: Traffic filter: ``"real"``, ``"bot"``, or ``"all"``.
        domain_name: Restrict results to a specific custom domain.
    """

    days: int
    start_date: str
    end_date: str
    bot_filter: Literal["real", "bot", "all"]
    domain_name: str


class GeoAnalyticsEntry(TypedDict):
    """A single row in geographic analytics results.

    Attributes:
        country: Full country name (e.g. ``"United States"``).
        country_code: ISO 3166-1 alpha-2 code (e.g. ``"US"``).
        clicks: Total clicks from this country.
        unique_visitors: Unique visitors from this country.
    """

    country: str
    country_code: str
    clicks: int
    unique_visitors: int


class DeviceAnalyticsParams(TypedDict, total=False):
    """Query parameters for device/browser analytics.

    Attributes:
        days: Rolling window in days.
        start_date: ISO-8601 start date (inclusive).
        end_date: ISO-8601 end date (inclusive).
        bot_filter: Traffic filter: ``"real"``, ``"bot"``, or ``"all"``.
        domain_name: Restrict results to a specific custom domain.
    """

    days: int
    start_date: str
    end_date: str
    bot_filter: Literal["real", "bot", "all"]
    domain_name: str


class DeviceAnalyticsEntry(TypedDict):
    """A single row in device analytics results.

    Attributes:
        device_type: Device category (e.g. ``"desktop"``, ``"mobile"``).
        browser: Browser name (e.g. ``"Chrome"``, ``"Safari"``).
        os: Operating system (e.g. ``"Windows"``, ``"iOS"``).
        clicks: Total clicks from this device/browser/OS combination.
    """

    device_type: str
    browser: str
    os: str
    clicks: int


class ReferrerAnalyticsParams(TypedDict, total=False):
    """Query parameters for referrer analytics.

    Attributes:
        days: Rolling window in days.
        start_date: ISO-8601 start date (inclusive).
        end_date: ISO-8601 end date (inclusive).
        bot_filter: Traffic filter: ``"real"``, ``"bot"``, or ``"all"``.
        domain_name: Restrict results to a specific custom domain.
    """

    days: int
    start_date: str
    end_date: str
    bot_filter: Literal["real", "bot", "all"]
    domain_name: str


class ReferrerAnalyticsEntry(TypedDict):
    """A single row in referrer analytics results.

    Attributes:
        referrer: Referrer domain or URL (e.g. ``"google.com"``).
        clicks: Total clicks from this referrer.
        unique_visitors: Unique visitors from this referrer.
    """

    referrer: str
    clicks: int
    unique_visitors: int


class HourlyAnalyticsParams(TypedDict, total=False):
    """Query parameters for hourly click distribution analytics.

    Attributes:
        days: Rolling window in days.
        start_date: ISO-8601 start date (inclusive).
        end_date: ISO-8601 end date (inclusive).
        bot_filter: Traffic filter: ``"real"``, ``"bot"``, or ``"all"``.
        domain_name: Restrict results to a specific custom domain.
    """

    days: int
    start_date: str
    end_date: str
    bot_filter: Literal["real", "bot", "all"]
    domain_name: str


class HourlyAnalyticsEntry(TypedDict):
    """A single hour bucket in hourly analytics results.

    Attributes:
        hour: Hour of the day in UTC (0-23).
        clicks: Total clicks during this hour.
        unique_visitors: Unique visitors during this hour.
    """

    hour: int
    clicks: int
    unique_visitors: int


# --------------------------------------------------------------------------
# Domains
# --------------------------------------------------------------------------

class Domain(TypedDict, total=False):
    """A custom domain registered with the organisation.

    Attributes:
        id: Unique domain identifier.
        domain: The domain name (e.g. ``"links.example.com"``).
        is_verified: Whether DNS verification has been completed.
        is_default: Whether this is the organisation's default domain.
        created_at: ISO-8601 creation timestamp.
    """

    id: str
    domain: str
    is_verified: bool
    is_default: bool
    created_at: str


# --------------------------------------------------------------------------
# Webhook Event Types
# --------------------------------------------------------------------------

WebhookEventType = Literal[
    "link.created",
    "link.updated",
    "link.deleted",
    "link.expired",
    "domain.verified",
    "domain.expired",
    "domain.suspended",
    "api_key.created",
    "api_key.revoked",
    "team.member_added",
    "team.member_removed",
    "subscription.upgraded",
    "subscription.downgraded",
    "bulk_import.completed",
    "conversion",
]

WEBHOOK_EVENTS: Dict[str, str] = {
    "LINK_CREATED": "link.created",
    "LINK_UPDATED": "link.updated",
    "LINK_DELETED": "link.deleted",
    "LINK_EXPIRED": "link.expired",
    "DOMAIN_VERIFIED": "domain.verified",
    "DOMAIN_EXPIRED": "domain.expired",
    "DOMAIN_SUSPENDED": "domain.suspended",
    "API_KEY_CREATED": "api_key.created",
    "API_KEY_REVOKED": "api_key.revoked",
    "TEAM_MEMBER_ADDED": "team.member_added",
    "TEAM_MEMBER_REMOVED": "team.member_removed",
    "SUBSCRIPTION_UPGRADED": "subscription.upgraded",
    "SUBSCRIPTION_DOWNGRADED": "subscription.downgraded",
    "BULK_IMPORT_COMPLETED": "bulk_import.completed",
    "CONVERSION": "conversion",
}

WEBHOOK_EVENT_CATEGORIES: Dict[str, List[str]] = {
    "links": [
        "link.created",
        "link.updated",
        "link.deleted",
        "link.expired",
    ],
    "domains": [
        "domain.verified",
        "domain.expired",
        "domain.suspended",
    ],
    "api_keys": [
        "api_key.created",
        "api_key.revoked",
    ],
    "team": [
        "team.member_added",
        "team.member_removed",
    ],
    "billing": [
        "subscription.upgraded",
        "subscription.downgraded",
    ],
    "bulk": [
        "bulk_import.completed",
    ],
    "journey": [
        "conversion",
    ],
}


class WebhookPayload(TypedDict, total=False):
    """Shape of a webhook delivery payload received at your endpoint.

    Your webhook endpoint receives POST requests with a JSON body
    matching this shape. Use the ``secret`` from webhook creation
    to verify the payload signature.

    Attributes:
        event: The event type string (e.g. ``"link.created"``).
        timestamp: ISO-8601 timestamp when the event occurred.
        data: Event-specific payload data (varies by event type).
    """

    event: str
    timestamp: str
    data: Dict[str, Any]


# --------------------------------------------------------------------------
# Webhooks
# --------------------------------------------------------------------------

class WebhookEndpoint(TypedDict, total=False):
    """A registered webhook endpoint.

    Attributes:
        id: Unique webhook endpoint identifier.
        url: The URL that receives webhook POST requests.
        events: List of subscribed event types (e.g.
            ``["link.created", "link.deleted"]``).
        is_active: Whether the endpoint is currently receiving events.
        description: User-supplied description of this endpoint.
        consecutive_failures: Number of consecutive delivery failures.
        last_failure_at: ISO-8601 timestamp of the most recent failure.
        created_at: ISO-8601 creation timestamp.
        updated_at: ISO-8601 last-modified timestamp.
        secret: Signing secret for verifying webhook payloads (only
            returned on creation).
    """

    id: str
    url: str
    events: List[str]
    is_active: bool
    description: str
    consecutive_failures: int
    last_failure_at: str
    created_at: str
    updated_at: str
    secret: str


class CreateWebhookParams(TypedDict, total=False):
    """Parameters for creating a new webhook endpoint.

    Attributes:
        url: The URL to receive webhook POST requests (required).
        events: Event types to subscribe to. Use constants from
            :data:`WEBHOOK_EVENTS` (required).
        description: Optional human-readable description.
    """

    url: str
    events: List[str]
    description: str


class UpdateWebhookParams(TypedDict, total=False):
    """Parameters for updating an existing webhook endpoint.

    Only include the fields you want to change.

    Attributes:
        url: New delivery URL.
        events: Replace the subscribed event types.
        description: New description.
        is_active: Enable or disable the endpoint.
    """

    url: str
    events: List[str]
    description: str
    is_active: bool


class WebhookDelivery(TypedDict, total=False):
    """Record of a single webhook delivery attempt.

    Attributes:
        id: Unique delivery identifier.
        event_type: The event type that was delivered (e.g.
            ``"link.created"``).
        status: Delivery status (e.g. ``"success"``, ``"failed"``).
        http_status: HTTP response status code from the endpoint.
        attempt_number: Which attempt this was (1-based).
        created_at: ISO-8601 timestamp when the delivery was queued.
        delivered_at: ISO-8601 timestamp when delivery completed.
    """

    id: str
    event_type: str
    status: str
    http_status: int
    attempt_number: int
    created_at: str
    delivered_at: str


class ListWebhookDeliveriesParams(TypedDict, total=False):
    """Pagination parameters for listing webhook deliveries.

    Attributes:
        page: Page number (1-based).
        limit: Maximum items per page.
    """

    page: int
    limit: int


# --------------------------------------------------------------------------
# Journey
# --------------------------------------------------------------------------

class JourneyEvent(TypedDict, total=False):
    """A single visitor journey event to ingest.

    Attributes:
        link_id: UUID of the QCK link. Read from ``?qck_link=`` URL param.
        visitor_id: Unique visitor identifier (user-managed).
        session_id: Session identifier (optional, enables session analytics).
        event_type: Type of event.
        event_name: Event name for custom/conversion events.
        page_url: Page URL (web) or screen/route name (mobile/server).
        page_title: Page or screen title.
        scroll_percent: Scroll depth percentage (0-100).
        time_on_page: Time spent on the page in seconds.
        timestamp: ISO-8601 timestamp of the event.
        conversion_name: Conversion name (for conversion events).
        revenue_cents: Revenue in cents (e.g. $49.99 = 4999).
        currency: ISO 4217 currency code (e.g. ``"USD"``).
        country_code: 2-char ISO 3166-1 country code.
        city: City name.
        region: State/province.
        device_type: Device type (e.g. ``"mobile"``, ``"desktop"``).
        browser: Browser name.
        browser_version: Browser version.
        os: Operating system name.
        os_version: OS version.
        properties: Arbitrary properties (stored in ClickHouse JSON column).
    """

    link_id: str
    visitor_id: str
    session_id: str
    event_type: Literal["page_view", "scroll_depth", "time_on_page", "custom", "conversion"]
    event_name: str
    page_url: str
    page_title: str
    scroll_percent: int
    time_on_page: int
    timestamp: str
    conversion_name: str
    revenue_cents: int
    currency: str
    country_code: str
    city: str
    region: str
    device_type: str
    browser: str
    browser_version: str
    os: str
    os_version: str
    properties: Dict[str, Any]


class IngestEventsParams(TypedDict):
    """Parameters for ingesting a batch of journey events.

    Attributes:
        events: List of journey events to ingest.
    """

    events: List[JourneyEvent]


class PageCount(TypedDict):
    """Page URL and its visit count in a journey summary.

    Attributes:
        url: Page URL.
        count: Number of visits to this page.
    """

    url: str
    count: int


class EventCount(TypedDict):
    """Event name and its occurrence count in a journey summary.

    Attributes:
        name: Event name.
        count: Number of times this event occurred.
    """

    name: str
    count: int


class JourneyLinkSummary(TypedDict):
    """Aggregated journey summary for a single link.

    Attributes:
        total_visitors: Unique visitors who interacted with this link.
        total_sessions: Total sessions recorded.
        total_events: Total events across all sessions.
        avg_session_duration_seconds: Average session length in seconds.
        top_pages: Most visited pages after clicking the link.
        top_events: Most frequent events after clicking the link.
    """

    total_visitors: int
    total_sessions: int
    total_events: int
    avg_session_duration_seconds: float
    top_pages: List[PageCount]
    top_events: List[EventCount]


class FunnelStep(TypedDict):
    """A single step in a funnel analysis result.

    Attributes:
        step_name: Name of this funnel step.
        visitors: Number of visitors who reached this step.
        conversion_rate: Percentage of the initial cohort that reached
            this step (0.0 to 100.0).
    """

    step_name: str
    visitors: int
    conversion_rate: float


class FunnelResult(TypedDict):
    """Result of a funnel analysis query.

    Attributes:
        steps: Ordered list of funnel steps with visitor counts and
            conversion rates.
        total_visitors: Number of visitors who entered the funnel
            (i.e. reached the first step).
    """

    steps: List[FunnelStep]
    total_visitors: int


class _FunnelParamsRequired(TypedDict):
    """Required fields for a funnel analysis query."""

    steps: List[str]


class FunnelParams(_FunnelParamsRequired, total=False):
    """Parameters for a funnel analysis query.

    Required: ``steps``.
    Optional: ``period``.

    Attributes:
        steps: Ordered list of event names defining the funnel stages.
        period: Time window: ``"7d"``, ``"30d"``, or ``"90d"``.
    """

    period: Literal["7d", "30d", "90d"]


class JourneyQueryParams(TypedDict, total=False):
    """Query parameters for journey summary endpoints.

    Attributes:
        period: Time window: ``"7d"``, ``"30d"``, or ``"90d"``.
    """

    period: Literal["7d", "30d", "90d"]


class SessionEvent(TypedDict):
    """A single event within a visitor session.

    Attributes:
        event_type: Type of event (e.g. ``"page_view"``, ``"custom"``).
        event_name: Human-readable event name.
        page_url: URL where the event occurred.
        timestamp: ISO-8601 timestamp of the event.
        scroll_percent: Scroll depth percentage (0-100).
        time_on_page: Time spent on the page in seconds.
    """

    event_type: str
    event_name: str
    page_url: str
    timestamp: str
    scroll_percent: int
    time_on_page: int


class SessionSummary(TypedDict, total=False):
    """Summary of a single visitor session.

    Attributes:
        visitor_id: Unique visitor identifier.
        session_id: Unique session identifier.
        session_start: ISO-8601 timestamp when the session began.
        session_end: ISO-8601 timestamp when the session ended.
        event_count: Total number of events in the session.
        pages_visited: List of page URLs visited during the session.
        events: Full list of events in chronological order.
    """

    visitor_id: str
    session_id: str
    session_start: str
    session_end: str
    event_count: int
    pages_visited: List[str]
    events: List[SessionEvent]


class ListJourneySessionsParams(TypedDict, total=False):
    """Pagination and filter parameters for listing journey sessions.

    Attributes:
        page: Page number (1-based).
        limit: Maximum items per page.
        visitor_id: Filter to sessions from a specific visitor.
        period: Time window: ``"7d"``, ``"30d"``, or ``"90d"``.
    """

    page: int
    limit: int
    visitor_id: str
    period: Literal["7d", "30d", "90d"]


class ListJourneyEventsParams(TypedDict, total=False):
    """Pagination and filter parameters for listing journey events.

    Attributes:
        page: Page number (1-based).
        limit: Maximum items per page.
        event_type: Filter to a specific event type.
        period: Time window: ``"7d"``, ``"30d"``, or ``"90d"``.
    """

    page: int
    limit: int
    event_type: str
    period: Literal["7d", "30d", "90d"]


# --------------------------------------------------------------------------
# Conversions
# --------------------------------------------------------------------------

ConversionPeriod = Literal["7d", "30d", "90d"]
ConversionInterval = Literal["hour", "day", "week", "month"]
ConversionDimension = Literal["device", "country", "link", "name"]


class ConversionScopeParams(TypedDict, total=False):
    """Scope/filter parameters shared by conversion endpoints.

    Attributes:
        period: Time window.
        domain_id: Filter to conversions from a specific domain.
        link_id: Filter to conversions from a specific link.
    """

    period: ConversionPeriod
    domain_id: str
    link_id: str


class ConversionTimeseriesParams(TypedDict, total=False):
    """Parameters for the conversion timeseries endpoint."""

    period: ConversionPeriod
    domain_id: str
    link_id: str
    interval: ConversionInterval


class ConversionBreakdownParams(TypedDict, total=False):
    """Parameters for the conversion breakdown endpoint."""

    period: ConversionPeriod
    domain_id: str
    link_id: str
    dimension: ConversionDimension


class _TrackConversionRequired(TypedDict):
    """Required fields for tracking a conversion event."""

    link_id: str
    visitor_id: str
    name: str


class TrackConversionParams(_TrackConversionRequired, total=False):
    """Parameters for tracking a conversion event.

    Required: ``link_id``, ``visitor_id``, ``name``.
    Optional: ``session_id``, ``revenue``, ``currency``, ``page_url``, ``properties``.
    """

    session_id: str
    revenue: float
    currency: str
    page_url: str
    properties: Dict[str, Any]


class ConversionSummary(TypedDict):
    """Aggregated conversion metrics for a period.

    Attributes:
        total_conversions: Total number of conversion events.
        unique_converters: Number of unique visitors who converted.
        total_revenue: Sum of all conversion revenue.
        average_order_value: Mean revenue per conversion.
        conversion_rate: Percentage of visitors who converted
            (0.0 to 100.0).
    """

    total_conversions: int
    unique_converters: int
    total_revenue: float
    average_order_value: float
    conversion_rate: float


class ConversionTimeseriesPoint(TypedDict):
    """A single data point in a conversion timeseries.

    Attributes:
        timestamp: ISO-8601 timestamp for this bucket.
        conversions: Number of conversions in this bucket.
        revenue: Total revenue in this bucket.
    """

    timestamp: str
    conversions: int
    revenue: float


class ConversionBreakdownEntry(TypedDict):
    """A single row in a conversion breakdown result.

    Attributes:
        label: Dimension value (e.g. country name, device type, or
            link title depending on the breakdown dimension).
        conversions: Number of conversions for this label.
        revenue: Total revenue for this label.
        conversion_rate: Conversion rate for this label (0.0 to 100.0).
    """

    label: str
    conversions: int
    revenue: float
    conversion_rate: float


class TimeToConvertBucket(TypedDict):
    """A single bucket in a time-to-convert distribution.

    Attributes:
        label: Human-readable time range (e.g. ``"0-1 min"``,
            ``"1-5 min"``).
        count: Number of conversions in this time range.
    """

    label: str
    count: int


class TimeToConvertData(TypedDict):
    """Time-to-convert distribution data.

    Shows how long visitors take from first click to conversion.

    Attributes:
        buckets: Distribution of conversions by time-to-convert range.
        average_seconds: Mean time to convert in seconds.
        median_seconds: Median time to convert in seconds.
    """

    buckets: List[TimeToConvertBucket]
    average_seconds: float
    median_seconds: float
