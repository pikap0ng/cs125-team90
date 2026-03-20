from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from studySpotRecommender.dataModels import SourceRecord
from .providerBase import BaseProvider


class FoursquareProvider(BaseProvider):
    name = "foursquare"
    endpoint = "https://places-api.foursquare.com/places/search"

    def fetch(self) -> list[SourceRecord]:
        if not self.config.foursquareApiKey:
            return []

        query = urlencode(
            {
                "ll": f"{self.config.uciLat},{self.config.uciLon}",
                "radius": self.config.radiusMeters,
                "query": "cafe library study",
                "limit": min(self.config.maxResultsPerSource, 50),
            }
        )
        req = Request(
            f"{self.endpoint}?{query}",
            headers={
                "Authorization": f"Bearer {self.config.foursquareApiKey}",
                "Accept": "application/json",
                "X-Places-Api-Version": "2025-06-17",
            },
        )

        try:
            with urlopen(req, timeout=self.config.requestTimeoutS) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as err:
            if self.config.verbose:
                body = err.read().decode("utf-8", errors="ignore")[:300]
                print(f"[provider] foursquare: HTTP {err.code} {err.reason} {body}")
            return []
        except URLError as err:
            if self.config.verbose:
                print(f"[provider] foursquare: URLError {err}")
            return []

        records: list[SourceRecord] = []
        for place in payload.get("results", []):
            lat = place.get("latitude", 0.0)
            lon = place.get("longitude", 0.0)
            if lat == 0.0 and lon == 0.0:
                geocodes = place.get("geocodes", {}).get("main", {})
                lat = geocodes.get("latitude", 0.0)
                lon = geocodes.get("longitude", 0.0)

            location = place.get("location", {})
            placeId = place.get("fsq_place_id") or place.get("fsq_id", "")

            records.append(
                SourceRecord(
                    provider=self.name,
                    sourceId=placeId,
                    name=place.get("name", "Unknown"),
                    latitude=lat,
                    longitude=lon,
                    address=location.get("formatted_address"),
                    transportNotes=f"Distance from query center: {place.get('distance', 'unknown')}m",
                    raw=place,
                )
            )
        return records
    