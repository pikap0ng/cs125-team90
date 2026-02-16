from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class AppConfig:
    """Runtime configuration for ingestion."""

    uci_lat: float = 33.6405
    uci_lon: float = -117.8443
    radius_miles: float = 5.0
    sqlite_path: str = "data/study_spots.db"
    request_timeout_s: int = 15
    max_results_per_source: int = 50
    user_agent: str = "uci-study-spot-pipeline/0.1"

    google_api_key: str | None = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY"))
    yelp_api_key: str | None = field(default_factory=lambda: os.getenv("YELP_API_KEY"))
    foursquare_api_key: str | None = field(default_factory=lambda: os.getenv("FOURSQUARE_API_KEY"))

    @property
    def radius_meters(self) -> int:
        return int(self.radius_miles * 1609.34)
