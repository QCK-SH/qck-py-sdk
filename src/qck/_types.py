"""QCK SDK type definitions."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypedDict


# --------------------------------------------------------------------------
# Generic response wrappers
# --------------------------------------------------------------------------

class ErrorDetail(TypedDict, total=False):
    code: str
    message: str


class ApiResponse(TypedDict, total=False):
    success: bool
    data: Any
    error: ErrorDetail


class PaginatedResponse(TypedDict):
    data: List[Any]
    total: int
    page: int
    limit: int


# --------------------------------------------------------------------------
# Links
# --------------------------------------------------------------------------

class Link(TypedDict, total=False):
    id: str
    short_code: str
    original_url: str
    short_url: str
    title: str
    description: str
    tags: List[str]
    is_active: bool
    expires_at: str
    click_count: int
    created_at: str
    updated_at: str


class CreateLinkParams(TypedDict, total=False):
    url: str
    custom_alias: str
    title: str
    description: str
    tags: List[str]
    expires_at: str
    domain_id: str


class UpdateLinkParams(TypedDict, total=False):
    original_url: str
    title: str
    description: str
    tags: List[str]
    is_active: bool
    expires_at: str


class ListLinksParams(TypedDict, total=False):
    page: int
    limit: int
    search: str


class BulkCreateParams(TypedDict):
    links: List[CreateLinkParams]


class LinkStats(TypedDict):
    total_clicks: int
    unique_clicks: int
    clicks_by_country: Dict[str, int]
    clicks_by_device: Dict[str, int]
    clicks_by_referrer: Dict[str, int]


# --------------------------------------------------------------------------
# Analytics
# --------------------------------------------------------------------------

class AnalyticsSummaryParams(TypedDict, total=False):
    start_date: str
    end_date: str
    days: int
    link_id: str


class CountryEntry(TypedDict):
    country: str
    clicks: int


class ReferrerEntry(TypedDict):
    referrer: str
    clicks: int


class DeviceEntry(TypedDict):
    device: str
    clicks: int


class AnalyticsSummary(TypedDict):
    total_clicks: int
    unique_visitors: int
    top_countries: List[CountryEntry]
    top_referrers: List[ReferrerEntry]
    top_devices: List[DeviceEntry]


class TimeseriesParams(TypedDict, total=False):
    start_date: str
    end_date: str
    days: int
    link_id: str
    interval: Literal["hour", "day", "week", "month"]


class TimeseriesPoint(TypedDict):
    timestamp: str
    clicks: int
    unique_visitors: int


# --------------------------------------------------------------------------
# Domains
# --------------------------------------------------------------------------

class Domain(TypedDict, total=False):
    id: str
    domain: str
    is_verified: bool
    is_default: bool
    created_at: str


# --------------------------------------------------------------------------
# Webhooks
# --------------------------------------------------------------------------

class WebhookEndpoint(TypedDict, total=False):
    id: str
    url: str
    events: List[str]
    description: str
    is_active: bool
    consecutive_failures: int
    created_at: str
    updated_at: str


class CreateWebhookParams(TypedDict, total=False):
    url: str
    events: List[str]
    description: str


class UpdateWebhookParams(TypedDict, total=False):
    url: str
    events: List[str]
    description: str
    is_active: bool


class WebhookDelivery(TypedDict, total=False):
    id: str
    event_type: str
    status: str
    http_status: int
    attempt_number: int
    created_at: str
    delivered_at: str


class ListWebhookDeliveriesParams(TypedDict, total=False):
    page: int
    limit: int


# --------------------------------------------------------------------------
# Journey
# --------------------------------------------------------------------------

class JourneyEvent(TypedDict, total=False):
    link_id: str
    visitor_id: str
    session_id: str
    event_type: Literal["page_view", "scroll_depth", "time_on_page", "custom", "conversion"]
    event_name: str
    page_url: str
    page_title: str
    referrer_url: str
    event_data: Dict[str, Any]
    scroll_percent: int
    time_on_page: int
    timestamp: str


class IngestEventsParams(TypedDict):
    events: List[JourneyEvent]


class PageCount(TypedDict):
    url: str
    count: int


class EventCount(TypedDict):
    name: str
    count: int


class JourneyLinkSummary(TypedDict):
    total_visitors: int
    total_sessions: int
    total_events: int
    avg_session_duration_seconds: float
    top_pages: List[PageCount]
    top_events: List[EventCount]


class FunnelStep(TypedDict):
    step_name: str
    visitors: int
    conversion_rate: float


class FunnelResult(TypedDict):
    steps: List[FunnelStep]
    total_visitors: int


class FunnelParams(TypedDict, total=False):
    steps: List[str]
    period: Literal["7d", "30d", "90d"]


class JourneyQueryParams(TypedDict, total=False):
    period: Literal["7d", "30d", "90d"]


class SessionEvent(TypedDict):
    event_type: str
    event_name: str
    page_url: str
    timestamp: str
    scroll_percent: int
    time_on_page: int


class SessionSummary(TypedDict, total=False):
    visitor_id: str
    session_id: str
    session_start: str
    session_end: str
    event_count: int
    pages_visited: List[str]
    events: List[SessionEvent]


class ListJourneySessionsParams(TypedDict, total=False):
    page: int
    limit: int
    visitor_id: str
    period: Literal["7d", "30d", "90d"]


class ListJourneyEventsParams(TypedDict, total=False):
    page: int
    limit: int
    event_type: str
    period: Literal["7d", "30d", "90d"]


# --------------------------------------------------------------------------
# Conversions
# --------------------------------------------------------------------------

ConversionPeriod = Literal["7d", "30d", "90d"]
ConversionInterval = Literal["hour", "day", "week", "month"]
ConversionDimension = Literal["source", "device", "country", "link", "name"]


class ConversionScopeParams(TypedDict, total=False):
    period: ConversionPeriod
    domain_id: str
    link_id: str


class ConversionTimeseriesParams(TypedDict, total=False):
    period: ConversionPeriod
    domain_id: str
    link_id: str
    interval: ConversionInterval


class ConversionBreakdownParams(TypedDict, total=False):
    period: ConversionPeriod
    domain_id: str
    link_id: str
    dimension: ConversionDimension


class TrackConversionParams(TypedDict, total=False):
    link_id: str
    visitor_id: str
    session_id: str
    name: str
    revenue: float
    currency: str
    page_url: str
    event_data: Dict[str, Any]


class ConversionSummary(TypedDict):
    total_conversions: int
    unique_converters: int
    total_revenue: float
    average_order_value: float
    conversion_rate: float


class ConversionTimeseriesPoint(TypedDict):
    timestamp: str
    conversions: int
    revenue: float


class ConversionBreakdownEntry(TypedDict):
    label: str
    conversions: int
    revenue: float
    conversion_rate: float
