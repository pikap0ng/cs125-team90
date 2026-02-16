from __future__ import annotations

import json
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from study_spot_recommender.Models import SourceRecord
from .Base import BaseProvider


class OSMProvider(BaseProvider):
    name = "osm"
    endpoint = "https://nominatim.openstreetmap.org/search"

    def fetch(self) -> list[SourceRecord]:
        query = urlencode(
            {
                "q": "cafe library study",
                "format": "jsonv2",
                "limit": self.config.max_results_per_source,
                "viewbox": "-117.92,33.72,-117.76,33.56",
                "bounded": 1,
                "addressdetails": 1,
                "extratags": 1,
            }
        )
        req = Request(f"{self.endpoint}?{query}", headers={"User-Agent": self.config.user_agent})

        try:
            with urlopen(req, timeout=self.config.request_timeout_s) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except URLError:
            return []

        records: list[SourceRecord] = []
        for place in payload:
            extratags = place.get("extratags", {})
            records.append(
                SourceRecord(
                    provider=self.name,
                    source_id=str(place.get("osm_id", "")),
                    name=place.get("name") or place.get("display_name", "Unknown").split(",")[0],
                    latitude=float(place.get("lat", 0.0)),
                    longitude=float(place.get("lon", 0.0)),
                    address=place.get("display_name"),
                    hours_text=extratags.get("opening_hours"),
                    wifi=extratags.get("internet_access"),
                    parking=extratags.get("parking"),
                    charging=extratags.get("socket:type2") or extratags.get("socket"),
                    transport_notes="OSM-derived candidate; routing should be hydrated separately",
                    raw=place,
                )
            )
        return records
