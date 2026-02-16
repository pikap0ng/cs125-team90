from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class SourceRecord:
    provider: str
    source_id: str
    name: str
    latitude: float
    longitude: float
    address: str | None = None
    hours_text: str | None = None
    open_now: bool | None = None
    parking: str | None = None
    wifi: str | None = None
    charging: str | None = None
    transport_notes: str | None = None
    on_campus: bool = False
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class CanonicalStudySpot:
    canonical_id: str
    name: str
    latitude: float
    longitude: float
    address: str | None
    on_campus: bool
    source_ids: dict[str, str]
    features: dict[str, Any]
    feature_provenance: dict[str, Any]
    confidence: dict[str, float]
    last_refreshed_at: str

    @classmethod
    def from_source(cls, record: SourceRecord) -> "CanonicalStudySpot":
        return cls(
            canonical_id=str(uuid4()),
            name=record.name,
            latitude=record.latitude,
            longitude=record.longitude,
            address=record.address,
            on_campus=record.on_campus,
            source_ids={record.provider: record.source_id},
            features={
                "hours_text": record.hours_text,
                "open_now": record.open_now,
                "parking": record.parking,
                "wifi": record.wifi,
                "charging": record.charging,
                "transport_notes": record.transport_notes,
            },
            feature_provenance={
                key: {
                    "source": record.provider,
                    "method": "api_or_scrape",
                    "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                }
                for key in ["hours_text", "open_now", "parking", "wifi", "charging", "transport_notes"]
            },
            confidence={
                "hours_text": 0.8 if record.hours_text else 0.0,
                "open_now": 0.9 if record.open_now is not None else 0.0,
                "parking": 0.7 if record.parking else 0.0,
                "wifi": 0.7 if record.wifi else 0.0,
                "charging": 0.5 if record.charging else 0.0,
                "transport_notes": 0.6 if record.transport_notes else 0.0,
            },
            last_refreshed_at=datetime.now(tz=timezone.utc).isoformat(),
        )
