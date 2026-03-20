from __future__ import annotations

import math
import re
from typing import Any, Iterable

from studySpotRecommender.dataModels import CanonicalStudySpot, SourceRecord


def normalizeName(name: str) -> str:
    return re.sub(r"\W+", "", name.lower())


def nameTokens(name: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", name.lower()) if token}


def nameSimilarity(nameA: str, nameB: str) -> float:
    tokensA = nameTokens(nameA)
    tokensB = nameTokens(nameB)
    if not tokensA or not tokensB:
        return 0.0
    return len(tokensA & tokensB) / len(tokensA | tokensB)


def haversineMeters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earthRadiusM = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    deltaPhi = math.radians(lat2 - lat1)
    deltaLambda = math.radians(lon2 - lon1)
    a = math.sin(deltaPhi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(deltaLambda / 2) ** 2
    return 2 * earthRadiusM * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _isMissingFeatureValue(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    return False


def deduplicate(records: Iterable[SourceRecord], distanceThresholdM: float = 50.0) -> list[CanonicalStudySpot]:
    canonicalSpots: list[CanonicalStudySpot] = []

    for record in records:
        matchedSpot = None
        normalizedRecordName = normalizeName(record.name)
        for candidate in canonicalSpots:
            exactName = normalizeName(candidate.name) == normalizedRecordName
            fuzzyName = nameSimilarity(candidate.name, record.name) >= 0.5
            geoClose = haversineMeters(record.latitude, record.longitude, candidate.latitude, candidate.longitude) <= distanceThresholdM
            if (exactName or fuzzyName) and geoClose:
                matchedSpot = candidate
                break

        if matchedSpot:
            matchedSpot.sourceIds[record.provider] = record.sourceId
            if _isMissingFeatureValue(matchedSpot.address) and not _isMissingFeatureValue(record.address):
                matchedSpot.address = record.address
            matchedSpot.onCampus = matchedSpot.onCampus or record.onCampus
            for featureKey, value in {
                "hoursText": record.hoursText,
                "openNow": record.openNow,
                "parking": record.parking,
                "wifi": record.wifi,
                "charging": record.charging,
                "transportNotes": record.transportNotes,
                "photoUrl": record.photoUrl,
            }.items():
                if _isMissingFeatureValue(value):
                    continue
                if _isMissingFeatureValue(matchedSpot.features.get(featureKey)):
                    matchedSpot.features[featureKey] = value
        else:
            canonicalSpots.append(CanonicalStudySpot.fromSource(record))

    return canonicalSpots