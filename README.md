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
# Track a conversion
client.conversions.track({
    "short_code": "abc123",            # required — link short code
    "visitor_id": "user-456",          # required — your user ID
    "name": "purchase",                # required — conversion name
    "session_id": "sess-789",          # optional
    "revenue": 49.99,                  # optional — dollars, converted to cents internally
    "currency": "USD",                 # optional (default: 'USD')
    "page_url": "/checkout",           # optional
    "properties": {"plan": "pro"},     # optional — stored in ClickHouse JSON column
})

# Conversion summary (org-wide or scoped)
summary = client.conversions.summary({
    "period": "30d",
    "short_code": "abc123",            # optional — scope to a link
})

# Conversion timeseries
points = client.conversions.timeseries({"period": "30d", "interval": "day"})

# Breakdown by dimension
by_name = client.conversions.breakdown({"dimension": "name", "period": "30d"})

# Time-to-convert analysis
ttc = client.conversions.time_to_convert({"period": "30d"})
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

Track visitor journeys from any platform — websites, mobile apps, server-side. After a user clicks your QCK short link, they're redirected with `?qck_id=<short_code>` in the URL.

**Event types** (Enum — must be one of these):

| Type | Use for | Key fields |
|------|---------|------------|
| `page_view` | Page/screen loads | `page_url`, `page_title` |
| `scroll_depth` | Scroll tracking | `scroll_percent` (0-100) |
| `time_on_page` | Time on page/screen | `time_on_page` (seconds) |
| `custom` | Any user-defined event | `event_name`, `properties` |
| `conversion` | Purchase, signup, lead | `conversion_name`, `revenue_cents`, `currency` |

```python
# Ingest journey events (batch up to 100 per request)
client.journey.ingest({"events": [
    # Page view
    {
        "short_code": "abc123",
        "visitor_id": "user-456",
        "session_id": "sess-789",       # optional
        "event_type": "page_view",
        "page_url": "/pricing",
        "page_title": "Pricing",
    },
    # Scroll depth
    {
        "short_code": "abc123",
        "visitor_id": "user-456",
        "event_type": "scroll_depth",
        "page_url": "/pricing",
        "scroll_percent": 75,
    },
    # Custom event with properties
    {
        "short_code": "abc123",
        "visitor_id": "user-456",
        "event_type": "custom",
        "event_name": "cta_click",
        "page_url": "/pricing",
        "properties": {"button": "hero", "variant": "B"},
    },
    # Conversion with revenue
    {
        "short_code": "abc123",
        "visitor_id": "user-456",
        "event_type": "conversion",
        "conversion_name": "purchase",
        "revenue_cents": 4999,           # $49.99
        "currency": "USD",
        "properties": {"plan": "pro"},
    },
]})

# Context fields (all optional — your data)
client.journey.ingest({"events": [{
    "short_code": "abc123",
    "visitor_id": "user-456",
    "event_type": "page_view",
    "page_url": "/home",
    "country_code": "US",
    "device_type": "mobile",
    "browser": "Chrome",
    "os": "iOS",
    "os_version": "17.2",
}]})

# Journey summary
summary = client.journey.get_summary("abc123", {"period": "30d"})

# Funnel analysis
funnel = client.journey.get_funnel("abc123", {
    "steps": ["page_view", "cta_click", "purchase"],
    "period": "30d",
})

# List sessions
sessions = client.journey.list_sessions("abc123", {"period": "7d", "limit": 10})

# List events
events = client.journey.list_events("abc123", {"event_type": "custom", "period": "7d"})
```

**cURL example:**

```bash
curl -X POST https://qck.sh/public-api/v1/journey/events \
  -H "X-API-Key: qck_your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{"events":[{"short_code":"abc123","visitor_id":"user-456","event_type":"page_view","page_url":"/pricing"}]}'
```

#### Journey API Reference

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `ingest(params)` | `IngestEventsParams` | `None` | Batch ingest journey events (1-100) |
| `get_summary(short_code, params?)` | `str, JourneyQueryParams` | `JourneyLinkSummary` | Link journey summary |
| `get_funnel(short_code, params)` | `str, FunnelParams` | `FunnelResult` | Funnel analysis |
| `list_sessions(short_code, params?)` | `str, ListJourneySessionsParams` | `PaginatedResponse` | List visitor sessions |
| `list_events(short_code, params?)` | `str, ListJourneyEventsParams` | `PaginatedResponse` | List journey events |

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
