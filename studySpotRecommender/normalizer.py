from __future__ import annotations

import math
import re
from typing import Iterable

from studySpotRecommender.dataModels import CanonicalStudySpot, SourceRecord


def normalizeName(name: str) -> str:
    return re.sub(r"\W+", "", name.lower())


def haversineMeters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earthRadiusM = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    deltaPhi = math.radians(lat2 - lat1)
    deltaLambda = math.radians(lon2 - lon1)
    a = math.sin(deltaPhi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(deltaLambda / 2) ** 2
    return 2 * earthRadiusM * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def deduplicate(records: Iterable[SourceRecord], distanceThresholdM: float = 50.0) -> list[CanonicalStudySpot]:
    canonicalSpots: list[CanonicalStudySpot] = []

    for record in records:
        matchedSpot = None
        normalizedRecordName = normalizeName(record.name)
        for candidate in canonicalSpots:
            nameClose = normalizeName(candidate.name) == normalizedRecordName
            geoClose = haversineMeters(record.latitude, record.longitude, candidate.latitude, candidate.longitude) <= distanceThresholdM
            if nameClose and geoClose:
                matchedSpot = candidate
                break

        if matchedSpot:
            matchedSpot.sourceIds[record.provider] = record.sourceId
            for featureKey, value in {
                "hoursText": record.hoursText,
                "openNow": record.openNow,
                "parking": record.parking,
                "wifi": record.wifi,
                "charging": record.charging,
                "transportNotes": record.transportNotes,
            }.items():
                if value and not matchedSpot.features.get(featureKey):
                    matchedSpot.features[featureKey] = value
        else:
            canonicalSpots.append(CanonicalStudySpot.fromSource(record))

    return canonicalSpots
