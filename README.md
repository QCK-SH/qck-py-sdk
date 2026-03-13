# QCK Python SDK

Official Python SDK for the [QCK](https://qck.sh) API. Create short links, track conversions, query analytics, manage webhooks, and more.

[![PyPI](https://img.shields.io/pypi/v/qck-sdk)](https://pypi.org/project/qck-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Installation

```bash
pip install qck-sdk
```

## Quick Start

```python
from qck import QCK

client = QCK(api_key="qck_your_api_key")

# Create a short link
link = client.links.create({"url": "https://example.com"})
print(link["short_url"])  # https://qck.sh/abc123

# Get analytics
summary = client.analytics.summary({"days": 30})
print(f"{summary['total_clicks']} clicks, {summary['unique_visitors']} visitors")

client.close()
```

### Context Manager

```python
with QCK(api_key="qck_your_api_key") as client:
    links = client.links.list({"page": 1, "limit": 10})
    for link in links["data"]:
        print(f"{link['short_code']} → {link['original_url']}")
```

## Configuration

```python
client = QCK(
    api_key="qck_your_api_key",                     # Required — your API key
    base_url="https://api.qck.sh/public-api/v1",    # Optional — API base URL
    timeout=30,                                       # Optional — request timeout in seconds (default: 30)
    retries=3,                                        # Optional — automatic retries (default: 3)
)
```

| Option     | Type  | Default                                 | Description                     |
|------------|-------|-----------------------------------------|---------------------------------|
| `api_key`  | `str` | —                                       | **Required.** Your QCK API key  |
| `base_url` | `str` | `'https://api.qck.sh/public-api/v1'`    | API base URL                    |
| `timeout`  | `int` | `30`                                    | Request timeout in seconds      |
| `retries`  | `int` | `3`                                     | Max automatic retries           |

## Resources

### Links

Full CRUD operations for short links, plus bulk creation, stats, and OG image management.

```python
# Create a link
link = client.links.create({
    "url": "https://example.com",
    "custom_alias": "my-link",          # optional
    "title": "Example",                 # optional
    "description": "My link",           # optional
    "tags": ["marketing", "q1"],        # optional
    "expires_at": "2026-12-31T00:00:00Z",  # optional, ISO 8601
    "is_password_protected": True,      # optional
    "password": "s3cret",              # optional
    "domain_id": "dom_123",            # optional, custom domain
    # UTM parameters
    "utm_source": "twitter",           # optional
    "utm_medium": "social",            # optional
    "utm_campaign": "launch",          # optional
    "utm_term": "sdk",                 # optional
    "utm_content": "hero",             # optional
})

# List links (paginated)
result = client.links.list({
    "page": 1,
    "per_page": 25,
    "search": "example",              # optional, search by URL/title/alias
    "tags": ["marketing"],             # optional, filter by tags
    "is_active": True,                 # optional
    "has_password": False,             # optional
    "domain": "links.example.com",     # optional, filter by domain name
    "domain_id": "dom_123",            # optional, filter by domain ID
    "created_after": "2026-01-01",     # optional, ISO 8601
    "created_before": "2026-12-31",    # optional, ISO 8601
    "sort_by": "created_at",           # optional
    "sort_order": "desc",              # optional, 'asc' | 'desc'
})
# result["data"]: list of links, result["total"], result["page"], result["limit"]

# Get a single link
link = client.links.get("link_id")

# Update a link
updated = client.links.update("link_id", {
    "title": "New Title",
    "is_active": False,
    "tags": ["updated"],
    "url": "https://new-destination.com",
})

# Delete a link
client.links.delete("link_id")

# Bulk create
links = client.links.bulk_create([
    {"url": "https://example.com/a"},
    {"url": "https://example.com/b", "custom_alias": "b-link"},
    {"url": "https://example.com/c", "tags": ["batch"]},
])

# Get link stats
stats = client.links.get_stats("link_id")
# stats["total_clicks"], stats["unique_clicks"]
# stats["clicks_by_country"], stats["clicks_by_device"], stats["clicks_by_referrer"]

# Upload OG image
client.links.upload_og_image("link_id", "/path/to/image.png")

# Delete OG image
client.links.delete_og_image("link_id")
```

#### Links API Reference

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create(params)` | `CreateLinkParams` | `Link` | Create a new short link |
| `list(params?)` | `ListLinksParams` | `PaginatedResponse` | List links with filters |
| `get(link_id)` | `str` | `Link` | Get a link by ID |
| `update(link_id, params)` | `str, UpdateLinkParams` | `Link` | Update a link |
| `delete(link_id)` | `str` | `None` | Delete a link |
| `bulk_create(links)` | `list[CreateLinkParams]` | `list[Link]` | Create multiple links |
| `get_stats(link_id)` | `str` | `LinkStats` | Get click statistics |
| `upload_og_image(link_id, file_path)` | `str, str` | `dict` | Upload OG image from file path |
| `delete_og_image(link_id)` | `str` | `None` | Remove OG image |

### Analytics

Query aggregate analytics across all links or filtered by domain.

```python
# Summary stats
summary = client.analytics.summary({
    "days": 30,                        # last N days (shorthand)
    # OR use date range:
    # "start_date": "2026-01-01",
    # "end_date": "2026-01-31",
    "bot_filter": "real",              # 'real' | 'bot' | 'all' (default: 'real')
    "domain_name": "links.example.com",  # optional, filter by domain
})
# summary["total_clicks"], summary["unique_visitors"], summary["total_links"]
# summary["today_clicks"], summary["yesterday_clicks"], summary["active_links"]

# Timeseries data
points = client.analytics.timeseries({"days": 7})
for point in points:
    print(f"{point['timestamp']}: {point['clicks']} clicks, {point['unique_visitors']} unique")

# Geographic breakdown
geo = client.analytics.geo({"days": 30})
for entry in geo:
    print(f"{entry['country']} ({entry['country_code']}): {entry['clicks']} clicks")

# Device breakdown
devices = client.analytics.devices({"days": 30})
for entry in devices:
    print(f"{entry['device_type']} / {entry['browser']} / {entry['os']}: {entry['clicks']}")

# Referrer breakdown
referrers = client.analytics.referrers({"days": 30})
for entry in referrers:
    print(f"{entry['referrer']}: {entry['clicks']} clicks")

# Hourly distribution
hourly = client.analytics.hourly({"days": 7})
for entry in hourly:
    print(f"{entry['hour']}:00 — {entry['clicks']} clicks")
```

#### Analytics API Reference

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `summary(params?)` | `AnalyticsSummaryParams` | `AnalyticsSummary` | Aggregate summary stats |
| `timeseries(params?)` | `TimeseriesParams` | `list[TimeseriesPoint]` | Clicks over time |
| `geo(params?)` | `GeoAnalyticsParams` | `list[GeoAnalyticsEntry]` | Geographic breakdown |
| `devices(params?)` | `DeviceAnalyticsParams` | `list[DeviceAnalyticsEntry]` | Device/browser/OS breakdown |
| `referrers(params?)` | `ReferrerAnalyticsParams` | `list[ReferrerAnalyticsEntry]` | Traffic source breakdown |
| `hourly(params?)` | `HourlyAnalyticsParams` | `list[HourlyAnalyticsEntry]` | Hourly click distribution |

### Conversions

Track and analyze conversion events tied to your links.

```python
# Track a conversion (server-side)
client.conversions.track({
    "link_id": "link_id",              # required
    "visitor_id": "vis_abc123",        # required
    "session_id": "sess_xyz",          # required
    "name": "purchase",                # required — conversion event name
    "revenue": 49.99,                  # optional
    "currency": "USD",                 # optional (default: 'USD')
    "page_url": "https://example.com/checkout",  # optional
    "event_data": {"plan": "pro"},     # optional — arbitrary metadata
})

# Conversion summary
summary = client.conversions.summary({
    "period": "30d",                   # '7d' | '30d' | '90d'
    "domain_id": "dom_123",           # optional
    "link_id": "link_id",             # optional
})
# summary["total_conversions"], summary["unique_converters"]
# summary["total_revenue"], summary["average_order_value"], summary["conversion_rate"]

# Conversion timeseries
points = client.conversions.timeseries({
    "period": "30d",
    "interval": "day",                 # 'hour' | 'day' | 'week' | 'month'
})
for point in points:
    print(f"{point['timestamp']}: {point['conversions']} conversions, ${point['revenue']}")

# Breakdown by dimension
by_source = client.conversions.breakdown({
    "dimension": "source",             # 'source' | 'device' | 'country' | 'link' | 'name'
    "period": "30d",
})
for entry in by_source:
    print(f"{entry['label']}: {entry['conversions']} ({entry['conversion_rate']:.1%})")

# Time-to-convert analysis
ttc = client.conversions.time_to_convert({"period": "30d"})
print(f"Average: {ttc['average_seconds']}s, Median: {ttc['median_seconds']}s")
for bucket in ttc["buckets"]:
    print(f"{bucket['label']}: {bucket['count']} conversions")
```

#### Conversions API Reference

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `track(params)` | `TrackConversionParams` | `None` | Record a conversion event |
| `summary(params?)` | `ConversionScopeParams` | `ConversionSummary` | Conversion summary stats |
| `timeseries(params?)` | `ConversionTimeseriesParams` | `list[ConversionTimeseriesPoint]` | Conversions over time |
| `breakdown(params)` | `ConversionBreakdownParams` | `list[ConversionBreakdownEntry]` | Breakdown by dimension |
| `time_to_convert(params?)` | `ConversionScopeParams` | `TimeToConvertData` | Time-to-convert distribution |

### Journey Tracking

Track user journeys across pages after clicking a link. Supports event ingestion, funnel analysis, and session replay.

```python
# Ingest journey events
client.journey.ingest({
    "events": [
        {
            "link_id": "link_id",           # required
            "visitor_id": "vis_abc123",     # required
            "session_id": "sess_1",         # required
            "event_type": "page_view",      # 'page_view' | 'scroll_depth' | 'time_on_page' | 'custom' | 'conversion'
            "page_url": "https://example.com/pricing",
            "page_title": "Pricing",        # optional
            "referrer_url": "https://google.com",  # optional
        },
        {
            "link_id": "link_id",
            "visitor_id": "vis_abc123",
            "session_id": "sess_1",
            "event_type": "scroll_depth",
            "page_url": "https://example.com/pricing",
            "scroll_percent": 75,           # 0-100
        },
        {
            "link_id": "link_id",
            "visitor_id": "vis_abc123",
            "session_id": "sess_1",
            "event_type": "custom",
            "event_name": "cta_click",      # required for 'custom' events
            "page_url": "https://example.com/pricing",
            "event_data": {"button": "hero"},  # optional metadata
        },
    ]
})

# Link journey summary
summary = client.journey.get_summary("link_id", {"period": "30d"})
# summary["total_visitors"], summary["total_sessions"], summary["total_events"]
# summary["avg_session_duration_seconds"]
# summary["top_pages"]: [{"url": ..., "count": ...}]
# summary["top_events"]: [{"name": ..., "count": ...}]

# Funnel analysis
funnel = client.journey.get_funnel("link_id", {
    "steps": ["page_view", "cta_click", "purchase"],
    "period": "30d",
})
# funnel["total_visitors"]
for step in funnel["steps"]:
    print(f"{step['step_name']}: {step['visitors']} ({step['conversion_rate']:.1%})")

# List sessions (paginated)
sessions = client.journey.list_sessions("link_id", {
    "period": "7d",
    "limit": 10,
    "visitor_id": "vis_abc123",    # optional, filter by visitor
})
# sessions["data"]: list of SessionSummary

# List events (paginated)
events = client.journey.list_events("link_id", {
    "event_type": "custom",        # optional filter
    "period": "7d",
    "limit": 50,
})
# events["data"]: list of JourneyEvent
```

#### Journey API Reference

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `ingest(params)` | `IngestEventsParams` | `None` | Batch ingest journey events |
| `get_summary(link_id, params?)` | `str, JourneyQueryParams` | `JourneyLinkSummary` | Link journey summary |
| `get_funnel(link_id, params)` | `str, FunnelParams` | `FunnelResult` | Funnel analysis |
| `list_sessions(link_id, params?)` | `str, ListJourneySessionsParams` | `PaginatedResponse` | List visitor sessions |
| `list_events(link_id, params?)` | `str, ListJourneyEventsParams` | `PaginatedResponse` | List journey events |

### Webhooks

Create, manage, and test webhook endpoints to receive real-time notifications.

```python
from qck import WEBHOOK_EVENTS, WEBHOOK_EVENT_CATEGORIES

# Create a webhook
webhook = client.webhooks.create({
    "url": "https://example.com/webhook",
    "events": [WEBHOOK_EVENTS["LINK_CREATED"], WEBHOOK_EVENTS["LINK_DELETED"]],
    "description": "Production webhook",  # optional
})
# webhook["id"], webhook["secret"] (for signature verification)

# Subscribe to all link events
all_links = client.webhooks.create({
    "url": "https://example.com/webhook",
    "events": WEBHOOK_EVENT_CATEGORIES["links"],
})

# List all webhooks
webhooks = client.webhooks.list()

# Get a webhook
wh = client.webhooks.get("webhook_id")

# Update a webhook
updated = client.webhooks.update("webhook_id", {
    "events": [WEBHOOK_EVENTS["LINK_CREATED"]],
    "is_active": False,
})

# Delete a webhook
client.webhooks.delete("webhook_id")

# View delivery history (paginated)
deliveries = client.webhooks.list_deliveries("webhook_id", {
    "page": 1,
    "limit": 20,
})
# deliveries["data"]: list of WebhookDelivery

# Send a test event
client.webhooks.test("webhook_id")
```

#### Webhook Events

| Key | Value | Category |
|-----|-------|----------|
| `LINK_CREATED` | `link.created` | links |
| `LINK_UPDATED` | `link.updated` | links |
| `LINK_DELETED` | `link.deleted` | links |
| `LINK_EXPIRED` | `link.expired` | links |
| `DOMAIN_VERIFIED` | `domain.verified` | domains |
| `DOMAIN_EXPIRED` | `domain.expired` | domains |
| `DOMAIN_SUSPENDED` | `domain.suspended` | domains |
| `API_KEY_CREATED` | `api_key.created` | api_keys |
| `API_KEY_REVOKED` | `api_key.revoked` | api_keys |
| `TEAM_MEMBER_ADDED` | `team.member_added` | team |
| `TEAM_MEMBER_REMOVED` | `team.member_removed` | team |
| `SUBSCRIPTION_UPGRADED` | `subscription.upgraded` | billing |
| `SUBSCRIPTION_DOWNGRADED` | `subscription.downgraded` | billing |
| `BULK_IMPORT_COMPLETED` | `bulk_import.completed` | bulk |

Use `WEBHOOK_EVENT_CATEGORIES` to subscribe to all events in a category:

```python
WEBHOOK_EVENT_CATEGORIES["links"]    # all link events
WEBHOOK_EVENT_CATEGORIES["domains"]  # all domain events
WEBHOOK_EVENT_CATEGORIES["team"]     # all team events
WEBHOOK_EVENT_CATEGORIES["billing"]  # all billing events
```

#### Webhooks API Reference

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create(params)` | `CreateWebhookParams` | `WebhookEndpoint` | Create a webhook endpoint |
| `list()` | — | `list[WebhookEndpoint]` | List all webhooks |
| `get(webhook_id)` | `str` | `WebhookEndpoint` | Get a webhook by ID |
| `update(webhook_id, params)` | `str, UpdateWebhookParams` | `WebhookEndpoint` | Update a webhook |
| `delete(webhook_id)` | `str` | `None` | Delete a webhook |
| `list_deliveries(webhook_id, params?)` | `str, ListWebhookDeliveriesParams` | `PaginatedResponse` | Delivery history |
| `test(webhook_id)` | `str` | `None` | Send a test event |

### Domains

List custom domains configured for your organization.

```python
domains = client.domains.list("org_id")
for domain in domains:
    print(f"{domain['domain']} (verified: {domain['is_verified']}, default: {domain['is_default']})")
```

#### Domains API Reference

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `list(organization_id)` | `str` | `list[Domain]` | List organization domains |

## Error Handling

The SDK provides typed error classes for different failure modes:

```python
from qck import (
    QCK,
    QCKError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
)

client = QCK(api_key="qck_your_api_key")

try:
    link = client.links.get("nonexistent")
except NotFoundError:
    print("Link not found")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited — retry after {e.retry_after}s")
except ValidationError as e:
    print(f"Invalid request: {e}")
except QCKError as e:
    print(f"API error {e.status}: {e.code} — {e}")
```

### Error Classes

| Class | HTTP Status | Code | Attributes |
|-------|------------|------|------------|
| `QCKError` | any | varies | `status`, `code`, `message` |
| `AuthenticationError` | 401 | `AUTHENTICATION_ERROR` | — |
| `RateLimitError` | 429 | `RATE_LIMIT_ERROR` | `retry_after` (seconds) |
| `NotFoundError` | 404 | `NOT_FOUND` | — |
| `ValidationError` | 400 | `VALIDATION_ERROR` | — |

### Automatic Retries

The SDK automatically retries requests on:

- **Rate limits (429)** — respects `Retry-After` header, falls back to 60s
- **Network errors** — connection failures, DNS resolution errors
- **Timeouts** — request timeout exceeded

Retries use exponential backoff (capped at 120s). Rate limit retries respect the server's `Retry-After` header.

## Pagination

Methods that return lists use cursor-based pagination:

```python
result = client.links.list({"page": 1, "per_page": 25})

print(result["data"])   # list of links
print(result["total"])  # total number of items
print(result["page"])   # current page
print(result["limit"])  # items per page

# Iterate through all pages
all_links = []
page = 1
while True:
    result = client.links.list({"page": page, "per_page": 100})
    all_links.extend(result["data"])
    if len(all_links) >= result["total"]:
        break
    page += 1
```

## Type Safety

The SDK uses `TypedDict` for all request parameters and response types. Your IDE will provide autocompletion and type checking:

```python
from qck._types import (
    Link,
    CreateLinkParams,
    UpdateLinkParams,
    ListLinksParams,
    LinkStats,
    AnalyticsSummary,
    TimeseriesPoint,
    GeoAnalyticsEntry,
    DeviceAnalyticsEntry,
    ReferrerAnalyticsEntry,
    HourlyAnalyticsEntry,
    ConversionSummary,
    TrackConversionParams,
    JourneyEvent,
    FunnelResult,
    SessionSummary,
    WebhookEndpoint,
    WebhookPayload,
    Domain,
    PaginatedResponse,
)
```

## Requirements

- **Python 3.9+**
- **[httpx](https://www.python-httpx.org/)** — modern HTTP client

## License

MIT
