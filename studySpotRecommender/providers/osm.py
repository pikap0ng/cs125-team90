from __future__ import annotations

import hashlib
import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from studySpotRecommender.dataModels import SourceRecord
from .providerBase import BaseProvider

_DEFAULT_CACHE_TTL_S = 6 * 60 * 60

_CACHE_DIR = "data/osm_cache"


class OSMProvider(BaseProvider):
    name = "osm"
    endpoints = (
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://overpass.nchc.org.tw/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
    )

    def __init__(self, config):
        super().__init__(config)
        self.cacheTtlS = _DEFAULT_CACHE_TTL_S
        self.cacheDir = _CACHE_DIR

    def _buildQuery(self) -> str:
        radius = self.config.radiusMeters
        lat = self.config.uciLat
        lon = self.config.uciLon
        return f"""
[out:json][timeout:60];
(
  node(around:{radius},{lat},{lon})["amenity"~"cafe|library|study_space|coworking_space"];
  way(around:{radius},{lat},{lon})["amenity"~"cafe|library|study_space|coworking_space"];
  relation(around:{radius},{lat},{lon})["amenity"~"cafe|library|study_space|coworking_space"];
  node(around:{radius},{lat},{lon})["name"~"study|learning",i];
  way(around:{radius},{lat},{lon})["name"~"study|learning",i];
);
out center tags;
""".strip()

    def _cacheKey(self, query: str) -> str:
        """Generate a deterministic cache filename from the query string."""
        queryHash = hashlib.sha256(query.encode("utf-8")).hexdigest()[:16]
        return f"osm_{queryHash}.json"

    def _readCache(self, cacheFile: str) -> dict[str, object] | None:
        """Read cached Overpass response if it exists and is within TTL."""
        cachePath = os.path.join(self.cacheDir, cacheFile)
        if not os.path.exists(cachePath):
            return None

        try:
            fileAge = time.time() - os.path.getmtime(cachePath)
            if fileAge > self.cacheTtlS:
                if self.config.verbose:
                    print(f"[osm] cache expired ({fileAge:.0f}s old, TTL={self.cacheTtlS}s)")
                return None

            with open(cachePath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if self.config.verbose:
                elementCount = len(data.get("elements", []))
                print(f"[osm] using cached response ({elementCount} elements, {fileAge:.0f}s old)")
            return data
        except (json.JSONDecodeError, OSError) as err:
            if self.config.verbose:
                print(f"[osm] cache read error: {err}")
            return None

    def _writeCache(self, cacheFile: str, data: dict[str, object]) -> None:
        """Write Overpass response to cache."""
        try:
            os.makedirs(self.cacheDir, exist_ok=True)
            cachePath = os.path.join(self.cacheDir, cacheFile)
            with open(cachePath, "w", encoding="utf-8") as f:
                json.dump(data, f)
            if self.config.verbose:
                print(f"[osm] cached response to {cachePath}")
        except OSError as err:
            if self.config.verbose:
                print(f"[osm] cache write error: {err}")

    def _fetchFromEndpoints(self, query: str) -> dict[str, object]:
        """Try each Overpass endpoint in order, return first successful response."""
        payload = urlencode({"data": query}).encode("utf-8")

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
                    if self.config.verbose:
                        print(f"[osm] success from {endpoint}")
                    return responsePayload
            except HTTPError as error:
                print(f"[osm] HTTPError {error.code} {error.reason} {endpoint}")
                try:
                    print("[osm] body head:", error.read().decode("utf-8")[:300])
                except Exception:
                    pass
            except URLError as error:
                print(f"[osm] URLError {error} {endpoint}")
            except TimeoutError as error:
                print(f"[osm] TimeoutError {error} {endpoint}")
            except OSError as error:
                print(f"[osm] OSError {error} {endpoint}")
            except json.JSONDecodeError as error:
                print(f"[osm] JSONDecodeError {error} {endpoint}")

        return {}

    def fetch(self) -> list[SourceRecord]:
        query = self._buildQuery()
        cacheFile = self._cacheKey(query)

        # Try cache first
        responsePayload = self._readCache(cacheFile)

        # If cache miss or expired, fetch from endpoints
        if not responsePayload:
            responsePayload = self._fetchFromEndpoints(query)

            # Cache the successful response for next time
            if responsePayload and responsePayload.get("elements"):
                self._writeCache(cacheFile, responsePayload)

        if not responsePayload:
            if self.config.verbose:
                print("[osm] all endpoints failed and no cache available")
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