from __future__ import annotations

import json
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from study_spot_recommender.Models import SourceRecord
from .Base import BaseProvider


class YelpProvider(BaseProvider):
    name = "yelp"
    endpoint = "https://api.yelp.com/v3/businesses/search"

    def fetch(self) -> list[SourceRecord]:
        if not self.config.yelp_api_key:
            return []

        query = urlencode(
            {
                "latitude": self.config.uci_lat,
                "longitude": self.config.uci_lon,
                "radius": min(self.config.radius_meters, 40000),
                "limit": min(self.config.max_results_per_source, 50),
                "categories": "coffee,coffeeroasteries,libraries",
            }
        )
        req = Request(
            f"{self.endpoint}?{query}",
            headers={"Authorization": f"Bearer {self.config.yelp_api_key}"},
        )

        try:
            with urlopen(req, timeout=self.config.request_timeout_s) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except URLError:
            return []

        records: list[SourceRecord] = []
        for business in payload.get("businesses", []):
            location = business.get("location", {})
            coordinates = business.get("coordinates", {})
            records.append(
                SourceRecord(
                    provider=self.name,
                    source_id=business.get("id", ""),
                    name=business.get("name", "Unknown"),
                    latitude=coordinates.get("latitude", 0.0),
                    longitude=coordinates.get("longitude", 0.0),
                    address=", ".join(location.get("display_address", [])) if location else None,
                    transport_notes="Yelp attribute hydration can enrich noise/wifi/parking",
                    raw=business,
                )
            )
        return records
