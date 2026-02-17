# QCK Python SDK

Official Python SDK for the [QCK](https://qck.sh) API. Create short links, track conversions, query analytics, and manage webhooks.

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
from qck import QCK

with QCK(api_key="qck_your_api_key") as client:
    links = client.links.list({"page": 1, "limit": 10})
    for link in links["data"]:
        print(f"{link['short_code']} → {link['original_url']}")
```

## Resources

### Links

```python
# Create
link = client.links.create({
    "url": "https://example.com",
    "custom_alias": "my-link",
    "title": "Example",
    "tags": ["marketing", "q1"],
    "expires_at": "2026-12-31T00:00:00Z",
    "domain_id": "dom_123",  # optional custom domain
})

# List
result = client.links.list({"page": 1, "limit": 25, "search": "example"})

# Get / Update / Delete
link = client.links.get("link_id")
link = client.links.update("link_id", {"title": "New Title", "is_active": False})
client.links.delete("link_id")

# Bulk create
links = client.links.bulk_create([
    {"url": "https://example.com/a"},
    {"url": "https://example.com/b"},
    {"url": "https://example.com/c"},
])

# Stats
stats = client.links.get_stats("link_id")
print(f"{stats['total_clicks']} total, {stats['unique_clicks']} unique")
```

### Analytics

```python
# Summary
summary = client.analytics.summary({
    "days": 30,
    "link_id": "link_id",  # optional, omit for org-wide
})

# Timeseries
points = client.analytics.timeseries({
    "days": 7,
    "interval": "day",
})
for point in points:
    print(f"{point['timestamp']}: {point['clicks']} clicks")
```

### Conversions

```python
# Track a conversion (server-side)
client.conversions.track({
    "link_id": "link_id",
    "visitor_id": "vis_abc123",
    "name": "purchase",
    "revenue": 49.99,
    "currency": "USD",
    "event_data": {"plan": "pro"},
})

# Query conversion metrics
summary = client.conversions.summary({"period": "30d"})
print(f"{summary['total_conversions']} conversions, ${summary['total_revenue']:.2f} revenue")

# Timeseries
points = client.conversions.timeseries({
    "period": "30d",
    "interval": "day",
})

# Breakdown by dimension
by_source = client.conversions.breakdown({
    "dimension": "source",
    "period": "30d",
})
for entry in by_source:
    print(f"{entry['label']}: {entry['conversions']} ({entry['conversion_rate']:.1%})")
```

### Journey Tracking

```python
# Ingest events
client.journey.ingest({
    "events": [
        {
            "link_id": "link_id",
            "visitor_id": "vis_abc123",
            "session_id": "sess_1",
            "event_type": "page_view",
            "page_url": "https://example.com/pricing",
            "page_title": "Pricing",
        },
        {
            "link_id": "link_id",
            "visitor_id": "vis_abc123",
            "session_id": "sess_1",
            "event_type": "custom",
            "event_name": "cta_click",
            "page_url": "https://example.com/pricing",
        },
    ]
})

# Link journey summary
summary = client.journey.get_summary("link_id", {"period": "30d"})
print(f"{summary['total_visitors']} visitors across {summary['total_sessions']} sessions")

# Funnel analysis
funnel = client.journey.get_funnel("link_id", {
    "steps": ["page_view", "cta_click", "purchase"],
    "period": "30d",
})
for step in funnel["steps"]:
    print(f"{step['step_name']}: {step['visitors']} ({step['conversion_rate']:.1%})")

# List sessions and events
sessions = client.journey.list_sessions("link_id", {"period": "7d", "limit": 10})
events = client.journey.list_events("link_id", {"event_type": "custom", "limit": 50})
```

### Webhooks

```python
# Create
webhook = client.webhooks.create({
    "url": "https://example.com/webhook",
    "events": ["link.clicked", "link.created"],
    "description": "Production webhook",
})

# List / Get / Update / Delete
webhooks = client.webhooks.list()
webhook = client.webhooks.get("webhook_id")
webhook = client.webhooks.update("webhook_id", {"is_active": False})
client.webhooks.delete("webhook_id")

# View deliveries
deliveries = client.webhooks.list_deliveries("webhook_id", {"limit": 20})

# Send test event
client.webhooks.test("webhook_id")
```

### Domains

```python
domains = client.domains.list("org_id")
for domain in domains:
    print(f"{domain['domain']} (verified: {domain['is_verified']})")
```

## Configuration

```python
client = QCK(
    api_key="qck_your_api_key",
    base_url="https://api.qck.sh/public-api/v1",  # default
    timeout=30,   # seconds, default 30
    retries=3,    # automatic retries, default 3
)
```

## Error Handling

```python
from qck import QCK, AuthenticationError, RateLimitError, NotFoundError, ValidationError, QCKError

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

Errors are automatically retried for rate limits (429) and network failures with exponential backoff.

## Requirements

- Python 3.9+
- [httpx](https://www.python-httpx.org/)

## License

MIT
