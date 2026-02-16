from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from studySpotRecommender.dataModels import SourceRecord
from .providerBase import BaseProvider


class GooglePlacesProvider(BaseProvider):
    name = "google"
    endpoint = "https://places.googleapis.com/v1/places:searchNearby"
    fieldMask = (
        "places.id,"
        "places.displayName,"
        "places.formattedAddress,"
        "places.location,"
        "places.types,"
        "places.primaryType,"
        "places.currentOpeningHours,"
        "places.regularOpeningHours,"
        "places.parkingOptions,"
        "places.outdoorSeating,"
        "places.accessibilityOptions"
    )

    def fetch(self) -> list[SourceRecord]:
        if not self.config.googleApiKey:
            if self.config.verbose:
                print("[provider] google: missing GOOGLE_API_KEY")
            return []

        payload = {
            "includedTypes": ["cafe", "library", "book_store"],
            "maxResultCount": self.config.maxResultsPerSource,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": self.config.uciLat, "longitude": self.config.uciLon},
                    "radius": self.config.radiusMeters,
                }
            },
        }
        req = Request(
            self.endpoint,
            method="POST",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.config.googleApiKey,
                "X-Goog-FieldMask": self.fieldMask,
            },
        )

        try:
            with urlopen(req, timeout=self.config.requestTimeoutS) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as err:
            if self.config.verbose:
                errorBody = err.read().decode("utf-8", errors="ignore")
                print(f"[provider] google: HTTP {err.code} {err.reason} {errorBody}")
            return []
        except URLError as err:
            if self.config.verbose:
                print(f"[provider] google: URLError {err.reason}")
            return []
        except json.JSONDecodeError as err:
            if self.config.verbose:
                print(f"[provider] google: invalid JSON response: {err}")
            return []

        records: list[SourceRecord] = []
        for place in payload.get("places", []):
            parkingObj = place.get("parkingOptions", {})
            parkingText = ", ".join([key for key, enabled in parkingObj.items() if enabled]) or None
            currentHours = place.get("currentOpeningHours", {})
            regularHours = place.get("regularOpeningHours", {})
            weekdayDescriptions = currentHours.get("weekdayDescriptions") or regularHours.get("weekdayDescriptions") or [None]
            records.append(
                SourceRecord(
                    provider=self.name,
                    sourceId=place.get("id", ""),
                    name=place.get("displayName", {}).get("text", "Unknown"),
                    latitude=place.get("location", {}).get("latitude", 0.0),
                    longitude=place.get("location", {}).get("longitude", 0.0),
                    address=place.get("formattedAddress"),
                    hoursText=weekdayDescriptions[0],
                    openNow=currentHours.get("openNow"),
                    parking=parkingText,
                    wifi=None,
                    charging="accessibility options available" if place.get("accessibilityOptions") else None,
                    transportNotes="Supports route-time hydration via Distance Matrix",
                    raw=place,
                )
            )
        return records
