from __future__ import annotations

import json
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from studySpotRecommender.dataModels import SourceRecord
from .providerBase import BaseProvider


class YelpProvider(BaseProvider):
    name = "yelp"
    endpoint = "https://api.yelp.com/v3/businesses/search"

    def fetch(self) -> list[SourceRecord]:
        if not self.config.yelpApiKey:
            return []

        query = urlencode(
            {
                "latitude": self.config.uciLat,
                "longitude": self.config.uciLon,
                "radius": min(self.config.radiusMeters, 40000),
                "limit": min(self.config.maxResultsPerSource, 50),
                "categories": "coffee,coffeeroasteries,libraries",
            }
        )
        req = Request(
            f"{self.endpoint}?{query}",
            headers={"Authorization": f"Bearer {self.config.yelpApiKey}"},
        )

        try:
            with urlopen(req, timeout=self.config.requestTimeoutS) as response:
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
                    sourceId=business.get("id", ""),
                    name=business.get("name", "Unknown"),
                    latitude=coordinates.get("latitude", 0.0),
                    longitude=coordinates.get("longitude", 0.0),
                    address=", ".join(location.get("display_address", [])) if location else None,
                    transportNotes="Yelp attribute hydration can enrich noise, wifi, and parking",
                    raw=business,
                )
            )
        return records
