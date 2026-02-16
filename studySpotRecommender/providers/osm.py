from __future__ import annotations

import json
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from studySpotRecommender.dataModels import SourceRecord
from .providerBase import BaseProvider


class OSMProvider(BaseProvider):
    name = "osm"
    endpoint = "https://nominatim.openstreetmap.org/search"

    def fetch(self) -> list[SourceRecord]:
        query = urlencode(
            {
                "q": "cafe library study",
                "format": "jsonv2",
                "limit": self.config.maxResultsPerSource,
                "viewbox": "-117.92,33.72,-117.76,33.56",
                "bounded": 1,
                "addressdetails": 1,
                "extratags": 1,
            }
        )
        req = Request(f"{self.endpoint}?{query}", headers={"User-Agent": self.config.userAgent})

        try:
            with urlopen(req, timeout=self.config.requestTimeoutS) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except URLError:
            return []

        records: list[SourceRecord] = []
        for place in payload:
            extraTags = place.get("extratags", {})
            records.append(
                SourceRecord(
                    provider=self.name,
                    sourceId=str(place.get("osm_id", "")),
                    name=place.get("name") or place.get("display_name", "Unknown").split(",")[0],
                    latitude=float(place.get("lat", 0.0)),
                    longitude=float(place.get("lon", 0.0)),
                    address=place.get("display_name"),
                    hoursText=extraTags.get("opening_hours"),
                    wifi=extraTags.get("internet_access"),
                    parking=extraTags.get("parking"),
                    charging=extraTags.get("socket:type2") or extraTags.get("socket"),
                    transportNotes="OSM-derived candidate; routing should be hydrated separately",
                    raw=place,
                )
            )
        return records
