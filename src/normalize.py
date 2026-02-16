from __future__ import annotations

import math
import re
from typing import Iterable

from study_spot_recommender.Models import CanonicalStudySpot, SourceRecord


def _normalize_name(name: str) -> str:
    return re.sub(r"\W+", "", name.lower())


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def deduplicate(records: Iterable[SourceRecord], distance_threshold_m: float = 50.0) -> list[CanonicalStudySpot]:
    canonical: list[CanonicalStudySpot] = []

    for record in records:
        matched = None
        normalized_record_name = _normalize_name(record.name)
        for candidate in canonical:
            name_close = _normalize_name(candidate.name) == normalized_record_name
            geo_close = _haversine_m(record.latitude, record.longitude, candidate.latitude, candidate.longitude) <= distance_threshold_m
            if name_close and geo_close:
                matched = candidate
                break

        if matched:
            matched.source_ids[record.provider] = record.source_id
            for feature_key, value in {
                "hours_text": record.hours_text,
                "open_now": record.open_now,
                "parking": record.parking,
                "wifi": record.wifi,
                "charging": record.charging,
                "transport_notes": record.transport_notes,
            }.items():
                if value and not matched.features.get(feature_key):
                    matched.features[feature_key] = value
        else:
            canonical.append(CanonicalStudySpot.from_source(record))

    return canonical
