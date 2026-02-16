from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class AppConfig:
    """Runtime configuration for ingestion."""

    uciLat: float = 33.6405
    uciLon: float = -117.8443
    radiusMiles: float = 5.0
    sqlitePath: str = "data/studySpots.db"
    requestTimeoutS: int = 15
    maxResultsPerSource: int = 50
    userAgent: str = "uci-study-spot-pipeline/0.1"

    googleApiKey: str | None = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY"))
    yelpApiKey: str | None = field(default_factory=lambda: os.getenv("YELP_API_KEY"))
    foursquareApiKey: str | None = field(default_factory=lambda: os.getenv("FOURSQUARE_API_KEY"))

    @property
    def radiusMeters(self) -> int:
        return int(self.radiusMiles * 1609.34)
