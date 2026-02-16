from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from studySpotRecommender.dataModels import SourceRecord
from .providerBase import BaseProvider


class OSMProvider(BaseProvider):
    name = "osm"
    endpoints = (
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://overpass.nchc.org.tw/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
    )

    def _buildQuery(self) -> str:
        radius = self.config.radiusMeters
        lat = self.config.uciLat
        lon = self.config.uciLon
        return f"""
[out:json][timeout:60];
(
  node(around:{radius},{lat},{lon})["amenity"~"cafe|library"];
  way(around:{radius},{lat},{lon})["amenity"~"cafe|library"];
);
out center tags;
""".strip()

    def fetch(self) -> list[SourceRecord]:
        payload = urlencode({"data": self._buildQuery()}).encode("utf-8")
        responsePayload: dict[str, object] = {}

        for endpoint in self.endpoints:
            req = Request(
                endpoint,
                method="POST",
                data=payload,
                headers={
                    "User-Agent": self.config.userAgent,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )

            try:
                with urlopen(req, timeout=max(self.config.requestTimeoutS, 60)) as response:
                    body = response.read().decode("utf-8")
                    responsePayload = json.loads(body)
                    break
            except HTTPError as error:
                print("[osm] HTTPError", error.code, error.reason, endpoint)
                try:
                    print("[osm] body head:", error.read().decode("utf-8")[:300])
                except Exception:
                    pass
            except URLError as error:
                print("[osm] URLError", error, endpoint)
            except json.JSONDecodeError as error:
                print("[osm] JSONDecodeError", error, endpoint)
                print("[osm] body head:", body[:300] if "body" in locals() else "<no body>")

        if not responsePayload:
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
