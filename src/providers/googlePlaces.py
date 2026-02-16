from __future__ import annotations

import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from study_spot_recommender.Models import SourceRecord
from .Base import BaseProvider


class GooglePlacesProvider(BaseProvider):
    name = "google"
    endpoint = "https://places.googleapis.com/v1/places:searchNearby"

    def fetch(self) -> list[SourceRecord]:
        if not self.config.google_api_key:
            return []

        payload = {
            "includedTypes": ["cafe", "library", "book_store"],
            "maxResultCount": self.config.max_results_per_source,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": self.config.uci_lat, "longitude": self.config.uci_lon},
                    "radius": self.config.radius_meters,
                }
            },
        }
        req = Request(
            self.endpoint,
            method="POST",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.config.google_api_key,
                "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.currentOpeningHours,places.parkingOptions,places.outdoorSeating,places.accessibilityOptions",
            },
        )

        try:
            with urlopen(req, timeout=self.config.request_timeout_s) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except URLError:
            return []

        records: list[SourceRecord] = []
        for place in payload.get("places", []):
            parking_obj = place.get("parkingOptions", {})
            parking_text = ", ".join([k for k, v in parking_obj.items() if v]) or None
            records.append(
                SourceRecord(
                    provider=self.name,
                    source_id=place.get("id", ""),
                    name=place.get("displayName", {}).get("text", "Unknown"),
                    latitude=place.get("location", {}).get("latitude", 0.0),
                    longitude=place.get("location", {}).get("longitude", 0.0),
                    address=place.get("formattedAddress"),
                    hours_text=(place.get("currentOpeningHours", {}).get("weekdayDescriptions") or [None])[0],
                    open_now=place.get("currentOpeningHours", {}).get("openNow"),
                    parking=parking_text,
                    wifi=None,
                    charging="wheelchair_accessible and seating likely available" if place.get("accessibilityOptions") else None,
                    transport_notes="Supports route-time hydration via Distance Matrix",
                    raw=place,
                )
            )
        return records
