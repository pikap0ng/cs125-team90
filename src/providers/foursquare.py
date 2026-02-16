from __future__ import annotations

import json
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from study_spot_recommender.Models import SourceRecord
from .Base import BaseProvider


class FoursquareProvider(BaseProvider):
    name = "foursquare"
    endpoint = "https://places-api.foursquare.com/places/search"

    def fetch(self) -> list[SourceRecord]:
        if not self.config.foursquare_api_key:
            return []

        query = urlencode(
            {
                "ll": f"{self.config.uci_lat},{self.config.uci_lon}",
                "radius": self.config.radius_meters,
                "query": "cafe library study",
                "limit": self.config.max_results_per_source,
            }
        )
        req = Request(
            f"{self.endpoint}?{query}",
            headers={
                "Authorization": f"Bearer {self.config.foursquare_api_key}",
                "Accept": "application/json",
            },
        )

        try:
            with urlopen(req, timeout=self.config.request_timeout_s) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except URLError:
            return []

        records: list[SourceRecord] = []
        for place in payload.get("results", []):
            geocodes = place.get("geocodes", {}).get("main", {})
            location = place.get("location", {})
            records.append(
                SourceRecord(
                    provider=self.name,
                    source_id=place.get("fsq_place_id", ""),
                    name=place.get("name", "Unknown"),
                    latitude=geocodes.get("latitude", 0.0),
                    longitude=geocodes.get("longitude", 0.0),
                    address=location.get("formatted_address"),
                    transport_notes=f"Distance from query center: {place.get('distance', 'unknown')}m",
                    raw=place,
                )
            )
        return records
