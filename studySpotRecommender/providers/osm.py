from __future__ import annotations

import json
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from studySpotRecommender.dataModels import SourceRecord
from .providerBase import BaseProvider


class OSMProvider(BaseProvider):
    name = "osm"
    endpoint = "https://overpass-api.de/api/interpreter"

    def _buildQuery(self) -> str:
        radius = self.config.radiusMeters
        lat = self.config.uciLat
        lon = self.config.uciLon
        return f"""
[out:json][timeout:25];
(
  node(around:{radius},{lat},{lon})["amenity"~"cafe|library|restaurant|fast_food"];
  way(around:{radius},{lat},{lon})["amenity"~"cafe|library|restaurant|fast_food"];
);
out center tags;
""".strip()

    def fetch(self) -> list[SourceRecord]:
        payload = urlencode({"data": self._buildQuery()}).encode("utf-8")
        req = Request(
            self.endpoint,
            method="POST",
            data=payload,
            headers={
                "User-Agent": self.config.userAgent,
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

        try:
            with urlopen(req, timeout=self.config.requestTimeoutS) as response:
                responsePayload = json.loads(response.read().decode("utf-8"))
        except (URLError, json.JSONDecodeError):
            return []

        records: list[SourceRecord] = []
        seenIds: set[str] = set()

        for element in responsePayload.get("elements", []):
            elementType = element.get("type")
            elementId = element.get("id")
            if elementType is None or elementId is None:
                continue

            sourceId = f"{elementType}:{elementId}"
            if sourceId in seenIds:
                continue
            seenIds.add(sourceId)

            tags = element.get("tags", {})
            center = element.get("center", {})
            latitude = element.get("lat", center.get("lat"))
            longitude = element.get("lon", center.get("lon"))
            if latitude is None or longitude is None:
                continue

            name = tags.get("name") or f"{tags.get('amenity', 'place').title()} {elementId}"
            addressParts = [
                tags.get("addr:housenumber"),
                tags.get("addr:street"),
                tags.get("addr:city"),
                tags.get("addr:postcode"),
            ]
            address = ", ".join(part for part in addressParts if part) or None

            records.append(
                SourceRecord(
                    provider=self.name,
                    sourceId=sourceId,
                    name=name,
                    latitude=float(latitude),
                    longitude=float(longitude),
                    address=address,
                    hoursText=tags.get("opening_hours"),
                    wifi=tags.get("internet_access") or tags.get("internet_access:fee"),
                    parking=tags.get("parking"),
                    charging=tags.get("socket") or tags.get("socket:type2"),
                    transportNotes=f"OSM amenity={tags.get('amenity', 'unknown')}",
                    raw=element,
                )
            )

            if len(records) >= self.config.maxResultsPerSource:
                break

        return records
