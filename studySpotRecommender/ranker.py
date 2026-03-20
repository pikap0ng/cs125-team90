from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from typing import Any

from studySpotRecommender.normalizer import haversineMeters
from studySpotRecommender.userModel import RequestContext, UserPreferences


# UCI campus center for distance calculations
_UCI_LAT = 33.6405
_UCI_LON = -117.8443

# Weights for each scoring dimension (sum to ~1.0 for interpretability)
_WEIGHTS = {
    "onCampus": 0.15,
    "vibe": 0.15,
    "wifi": 0.12,
    "parking": 0.12,
    "outlets": 0.08,
    "quiet": 0.08,
    "lateHours": 0.10,
    "distance": 0.10,
    "bookmark": 0.10,
}


@dataclass
class ScoredSpot:
    """A canonical spot with a computed relevance score and explanation."""

    canonicalId: str
    canonicalKey: str
    name: str
    latitude: float
    longitude: float
    address: str | None
    onCampus: bool
    features: dict[str, Any]
    score: float
    explanation: list[str]
    distanceMiles: float | None


def _parseClosingHour(hoursText: str | None) -> int | None:
    """Extract the closing hour (0-23) from a hours string like 'Monday: 7:00 AM - 11:00 PM'."""
    if not hoursText:
        return None
    match = re.search(
        r"(\d{1,2})(?::\d{2})?\s*(AM|PM|am|pm)\s*$",
        hoursText.strip(),
    )
    if not match:
        return None
    hour = int(match.group(1))
    period = match.group(2).upper()
    if period == "PM" and hour != 12:
        hour += 12
    elif period == "AM" and hour == 12:
        hour = 0
    return hour


def _guessVibe(name: str, features: dict[str, Any]) -> str:
    """Infer a vibe category from the spot name and features."""
    lower = name.lower()
    if any(word in lower for word in ("library", "study", "gateway", "learning")):
        return "library"
    if any(word in lower for word in ("cafe", "coffee", "tea", "bakery", "roaster")):
        return "cafe"
    if any(word in lower for word in ("park", "garden", "outdoor", "patio")):
        return "outdoor"
    return "other"


def _distanceMilesFromCampus(lat: float, lon: float) -> float:
    meters = haversineMeters(_UCI_LAT, _UCI_LON, lat, lon)
    return meters / 1609.34


def rankSpots(
    spots: list[dict[str, Any]],
    preferences: UserPreferences,
    context: RequestContext | None = None,
    bookmarkedKeys: set[str] | None = None,
    topK: int = 10,
) -> list[ScoredSpot]:
    """Score and rank canonical spots against user preferences and context.

    Each spot dict is expected to have the columns from the canonicalSpots table.
    Returns the top-k scored spots in descending score order.
    """
    if context is None:
        context = RequestContext()
    if bookmarkedKeys is None:
        bookmarkedKeys = set()

    scored: list[ScoredSpot] = []

    for spot in spots:
        features = spot.get("features", {})
        if isinstance(features, str):
            features = json.loads(features)

        name = spot.get("name", "")
        lat = spot.get("latitude", _UCI_LAT)
        lon = spot.get("longitude", _UCI_LON)
        onCampus = bool(spot.get("onCampus", False))
        canonicalKey = spot.get("canonicalKey", "")
        distMiles = _distanceMilesFromCampus(lat, lon)

        # ── hard filters ──
        if context.onCampusOnly and not onCampus:
            continue

        if preferences.maxDistanceMiles is not None and distMiles > preferences.maxDistanceMiles:
            continue

        # free-text query filter: if present, name must contain at least one query token
        if context.query:
            queryTokens = set(context.query.lower().split())
            nameLower = name.lower()
            if not any(token in nameLower for token in queryTokens):
                continue

        # ── scoring ──
        score = 0.0
        explanation: list[str] = []

        # on-campus match
        if preferences.preferOnCampus is True and onCampus:
            score += _WEIGHTS["onCampus"]
            explanation.append("on campus (+)")
        elif preferences.preferOnCampus is False and not onCampus:
            score += _WEIGHTS["onCampus"]
            explanation.append("off campus as preferred (+)")
        elif preferences.preferOnCampus is None:
            score += _WEIGHTS["onCampus"] * 0.5

        # vibe match
        spotVibe = _guessVibe(name, features)
        if preferences.preferredVibe and spotVibe == preferences.preferredVibe:
            score += _WEIGHTS["vibe"]
            explanation.append(f"vibe match: {spotVibe} (+)")
        elif preferences.preferredVibe is None:
            score += _WEIGHTS["vibe"] * 0.5

        # wifi
        wifiValue = features.get("wifi")
        hasWifi = wifiValue is not None and str(wifiValue).strip() != ""
        if preferences.needsWifi:
            if hasWifi:
                score += _WEIGHTS["wifi"]
                explanation.append("has wifi (+)")
            else:
                explanation.append("no wifi data (-)")
        else:
            score += _WEIGHTS["wifi"] * 0.5

        # parking
        parkingValue = features.get("parking")
        hasParking = parkingValue is not None and str(parkingValue).strip() != ""
        if preferences.needsParking:
            if hasParking:
                score += _WEIGHTS["parking"]
                explanation.append("has parking (+)")
            else:
                explanation.append("no parking data (-)")
        else:
            score += _WEIGHTS["parking"] * 0.5

        # outlets (inferred from charging field or vibe)
        chargingValue = features.get("charging")
        hasOutlets = chargingValue is not None and str(chargingValue).strip() != ""
        if preferences.needsOutlets:
            if hasOutlets or spotVibe == "library":
                score += _WEIGHTS["outlets"]
                explanation.append("likely has outlets (+)")
            else:
                explanation.append("outlet availability unknown (-)")
        else:
            score += _WEIGHTS["outlets"] * 0.5

        # quiet preference
        if preferences.preferQuiet:
            if spotVibe == "library":
                score += _WEIGHTS["quiet"]
                explanation.append("library environment, likely quiet (+)")
            elif spotVibe == "cafe":
                score += _WEIGHTS["quiet"] * 0.3
                explanation.append("cafe, moderate noise (-)")
            else:
                score += _WEIGHTS["quiet"] * 0.5
        else:
            score += _WEIGHTS["quiet"] * 0.5

        # late hours
        closingHour = _parseClosingHour(features.get("hoursText"))
        if preferences.preferLateHours:
            if closingHour is not None and closingHour >= 21:
                score += _WEIGHTS["lateHours"]
                explanation.append(f"open until {closingHour}:00 (+)")
            elif closingHour is not None:
                fraction = max(0, (closingHour - 17)) / 6.0
                score += _WEIGHTS["lateHours"] * fraction
                explanation.append(f"closes at {closingHour}:00")
            elif onCampus:
                score += _WEIGHTS["lateHours"] * 0.6
                explanation.append("campus spot, hours unknown")
            else:
                explanation.append("hours unknown (-)")
        else:
            score += _WEIGHTS["lateHours"] * 0.5

        # distance (closer is better, normalized 0-1 over 10 miles)
        distScore = max(0.0, 1.0 - (distMiles / 10.0))
        score += _WEIGHTS["distance"] * distScore
        if distMiles < 1.0:
            explanation.append(f"{distMiles:.1f} mi away, very close (+)")
        elif distMiles < 3.0:
            explanation.append(f"{distMiles:.1f} mi away (+)")
        else:
            explanation.append(f"{distMiles:.1f} mi away")

        # bookmark bonus
        if canonicalKey in bookmarkedKeys:
            score += _WEIGHTS["bookmark"]
            explanation.append("bookmarked (+)")

        # context: commute mode boost
        if context.commuteMode == "driving" and hasParking:
            score += 0.05
            explanation.append("parking available for driver (+)")
        elif context.commuteMode == "walking" and onCampus:
            score += 0.05
            explanation.append("walkable on campus (+)")

        scored.append(
            ScoredSpot(
                canonicalId=spot.get("canonicalId", ""),
                canonicalKey=canonicalKey,
                name=name,
                latitude=lat,
                longitude=lon,
                address=spot.get("address"),
                onCampus=onCampus,
                features=features,
                score=round(score, 4),
                explanation=explanation,
                distanceMiles=round(distMiles, 2),
            )
        )

    scored.sort(key=lambda s: s.score, reverse=True)
    return scored[:topK]
