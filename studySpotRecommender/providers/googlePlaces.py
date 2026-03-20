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
        "places.accessibilityOptions,"
        "places.photos"
    )

    # Only include place types where studying is reasonable
    includedTypeGroups = (
        ["library", "book_store", "cafe", "coffee_shop"],
        ["community_center", "university"],
    )

    # Any spot with at least one of these types is always kept, no matter what
    _STUDY_FRIENDLY_TYPES = {
        "library", "book_store", "cafe", "coffee_shop",
        "university", "community_center", "coworking_space",
    }

    # Spots whose primary type is one of these AND that have zero study-friendly types are rejected
    _EXCLUDE_PRIMARY_TYPES = {
        "steak_house", "seafood_restaurant", "pizza_restaurant",
        "sushi_restaurant", "barbecue_restaurant", "mexican_restaurant",
        "chinese_restaurant", "japanese_restaurant", "korean_restaurant",
        "thai_restaurant", "vietnamese_restaurant", "italian_restaurant",
        "american_restaurant", "indian_restaurant", "mediterranean_restaurant",
        "hamburger_restaurant", "ramen_restaurant", "sandwich_shop",
        "ice_cream_shop", "dessert_shop", "bar", "night_club",
        "meal_delivery", "meal_takeaway", "liquor_store",
        "fast_food_restaurant",
    }

    def _searchNearby(self, includedTypes: list[str], maxResultCount: int) -> dict[str, object] | None:
        payload = {
            "includedTypes": includedTypes,
            "maxResultCount": maxResultCount,
            "rankPreference": "POPULARITY",
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
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as err:
            if self.config.verbose:
                errorBody = err.read().decode("utf-8", errors="ignore")
                print(f"[provider] google: HTTP {err.code} {err.reason} {errorBody}")
            return None
        except URLError as err:
            if self.config.verbose:
                print(f"[provider] google: URLError {err.reason}")
            return None
        except json.JSONDecodeError as err:
            if self.config.verbose:
                print(f"[provider] google: invalid JSON response: {err}")
            return None

    @classmethod
    def _isStudyAppropriate(cls, place: dict) -> bool:
        placeTypes = set(place.get("types", []))
        primaryType = place.get("primaryType", "")
        name = place.get("displayName", {}).get("text", "").lower()

        # Step 1: any study-friendly type means automatic keep
        if placeTypes & cls._STUDY_FRIENDLY_TYPES:
            return True
        if primaryType in cls._STUDY_FRIENDLY_TYPES:
            return True

        # Step 2: name contains study-friendly keywords
        studyNameKeywords = [
            "library", "cafe", "coffee", "tea house", "study",
            "learning", "coworking", "book",
        ]
        if any(kw in name for kw in studyNameKeywords):
            return True

        # Step 3: explicit restaurant subcategory with no study type match
        if primaryType in cls._EXCLUDE_PRIMARY_TYPES:
            return False

        # Step 4: name-based rejection for obvious non-study spots
        excludeNamePatterns = [
            "steakhouse", "grill", "bbq", "barbecue", "sushi", "ramen",
            "pizza", "burger", "taco", "wings", "seafood", "buffet",
            "brewery", "pub ", " pub", "nightclub", "karaoke",
            "shake shack", "mcdonald", "chick-fil-a", "wendy",
            "panda express", "del taco", "jack in the box",
        ]
        if any(pattern in name for pattern in excludeNamePatterns):
            return False

        # Step 5: everything else passes
        return True

    def _buildPhotoUrl(self, place: dict) -> str | None:
        """Extract the first photo reference and resolve to a direct image URL.

        Uses skipHttpRedirect=true to get the resolved photoUri from the API
        instead of a 302 redirect, so Flutter gets a direct image link.
        """
        photos = place.get("photos", [])
        if not photos:
            return None

        photoName = photos[0].get("name")
        if not photoName:
            return None

        # Request the resolved URL via skipHttpRedirect
        mediaUrl = (
            f"https://places.googleapis.com/v1/{photoName}/media"
            f"?maxWidthPx=400&skipHttpRedirect=true&key={self.config.googleApiKey}"
        )

        try:
            req = Request(mediaUrl, headers={"Accept": "application/json"})
            with urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                resolvedUrl = data.get("photoUri")
                if resolvedUrl:
                    if self.config.verbose:
                        placeName = place.get("displayName", {}).get("text", "?")
                        print(f"[provider] google: resolved photo for {placeName}")
                    return resolvedUrl
        except Exception as err:
            if self.config.verbose:
                print(f"[provider] google: photo resolve failed: {err}")

        # Fallback to the redirect URL (Flutter follows 302s)
        return (
            f"https://places.googleapis.com/v1/{photoName}/media"
            f"?maxWidthPx=400&key={self.config.googleApiKey}"
        )

    def fetch(self) -> list[SourceRecord]:
        if not self.config.googleApiKey:
            if self.config.verbose:
                print("[provider] google: missing GOOGLE_API_KEY")
            return []

        records: list[SourceRecord] = []
        seenPlaceIds: set[str] = set()
        remaining = max(self.config.maxResultsPerSource, 1)

        for typeGroup in self.includedTypeGroups:
            if remaining <= 0:
                break
            payload = self._searchNearby(typeGroup, min(remaining, 20))
            if not payload:
                continue
            for place in payload.get("places", []):
                placeId = place.get("id", "")
                if not placeId or placeId in seenPlaceIds:
                    continue
                seenPlaceIds.add(placeId)

                if not self._isStudyAppropriate(place):
                    if self.config.verbose:
                        placeName = place.get("displayName", {}).get("text", "Unknown")
                        pType = place.get("primaryType", "?")
                        print(f"[provider] google: filtered out: {placeName} (primaryType={pType})")
                    continue

                parkingObj = place.get("parkingOptions", {})
                parkingText = ", ".join([key for key, enabled in parkingObj.items() if enabled]) or None
                currentHours = place.get("currentOpeningHours", {})
                regularHours = place.get("regularOpeningHours", {})
                weekdayDescriptions = currentHours.get("weekdayDescriptions") or regularHours.get("weekdayDescriptions") or [None]

                photoUrl = self._buildPhotoUrl(place)

                records.append(
                    SourceRecord(
                        provider=self.name,
                        sourceId=placeId,
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
                        photoUrl=photoUrl,
                        raw=place,
                    )
                )
                remaining -= 1
                if remaining <= 0:
                    break

        return records
