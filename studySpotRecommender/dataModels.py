from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
from typing import Any
from uuid import uuid4


STOPWORDS = {"the", "a", "an", "cafe", "coffee", "shop"}


def _normalizeNameTokens(name: str) -> str:
    tokens = [token for token in re.findall(r"[a-z0-9]+", name.lower()) if token not in STOPWORDS]
    return "-".join(tokens) or "unknown"


def buildCanonicalKey(name: str, latitude: float, longitude: float, precision: int = 4) -> str:
    roundedLat = round(latitude, precision)
    roundedLon = round(longitude, precision)
    return f"{_normalizeNameTokens(name)}:{roundedLat}:{roundedLon}"


@dataclass
class SourceRecord:
    provider: str
    sourceId: str
    name: str
    latitude: float
    longitude: float
    address: str | None = None
    hoursText: str | None = None
    openNow: bool | None = None
    parking: str | None = None
    wifi: str | None = None
    charging: str | None = None
    transportNotes: str | None = None
    onCampus: bool = False
    fetchedAt: str = field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class CanonicalStudySpot:
    canonicalId: str
    canonicalKey: str
    name: str
    latitude: float
    longitude: float
    address: str | None
    onCampus: bool
    sourceIds: dict[str, str]
    features: dict[str, Any]
    featureProvenance: dict[str, Any]
    confidence: dict[str, float]
    lastRefreshedAt: str

    @classmethod
    def fromSource(cls, record: SourceRecord) -> "CanonicalStudySpot":
        return cls(
            canonicalId=str(uuid4()),
            canonicalKey=buildCanonicalKey(record.name, record.latitude, record.longitude),
            name=record.name,
            latitude=record.latitude,
            longitude=record.longitude,
            address=record.address,
            onCampus=record.onCampus,
            sourceIds={record.provider: record.sourceId},
            features={
                "hoursText": record.hoursText,
                "openNow": record.openNow,
                "parking": record.parking,
                "wifi": record.wifi,
                "charging": record.charging,
                "transportNotes": record.transportNotes,
            },
            featureProvenance={
                key: {
                    "source": record.provider,
                    "method": "apiOrScrape",
                    "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                }
                for key in ["hoursText", "openNow", "parking", "wifi", "charging", "transportNotes"]
            },
            confidence={
                "hoursText": 0.8 if record.hoursText else 0.0,
                "openNow": 0.9 if record.openNow is not None else 0.0,
                "parking": 0.7 if record.parking else 0.0,
                "wifi": 0.7 if record.wifi else 0.0,
                "charging": 0.5 if record.charging else 0.0,
                "transportNotes": 0.6 if record.transportNotes else 0.0,
            },
            lastRefreshedAt=datetime.now(tz=timezone.utc).isoformat(),
        )
