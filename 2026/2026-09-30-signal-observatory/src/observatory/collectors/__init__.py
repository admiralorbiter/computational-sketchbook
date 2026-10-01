"""Platform-specific data collectors.

Each collector implements a common interface defined in base.py,
adapting platform APIs to the observatory's unified artifact model.
"""

from observatory.collectors.base import BaseCollector, CollectorCapabilities
from observatory.collectors.bluesky import BlueskyCollector
from observatory.collectors.footage import CitizenFootageCollector
from observatory.collectors.reddit import RedditCollector
from observatory.collectors.reviews import ReviewsCollector
from observatory.collectors.snapchat import SnapchatCollector
from observatory.collectors.web import WebCollector
from observatory.collectors.youtube import YouTubeCollector

__all__ = [
    "BaseCollector",
    "CollectorCapabilities",
    "BlueskyCollector",
    "CitizenFootageCollector",
    "RedditCollector",
    "ReviewsCollector",
    "SnapchatCollector",
    "WebCollector",
    "YouTubeCollector",
]
