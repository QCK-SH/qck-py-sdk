"""QCK SDK resource modules.

Each resource class provides methods that map to a group of related API
endpoints. Resource instances are created automatically by the
:class:`~qck.QCK` client and exposed as attributes (e.g.
``client.links``, ``client.analytics``).

Resources:
    LinksResource: Create, list, update, and delete short links.
    AnalyticsResource: Query click analytics summaries and timeseries.
    ConversionsResource: Track and query conversion events.
    DomainsResource: List custom domains.
    JourneyResource: Ingest events and query visitor journeys.
    WebhooksResource: Manage webhook endpoints and deliveries.
"""

from .analytics import AnalyticsResource
from .conversions import ConversionsResource
from .domains import DomainsResource
from .journey import JourneyResource
from .links import LinksResource
from .webhooks import WebhooksResource

__all__ = [
    "AnalyticsResource",
    "ConversionsResource",
    "DomainsResource",
    "JourneyResource",
    "LinksResource",
    "WebhooksResource",
]
