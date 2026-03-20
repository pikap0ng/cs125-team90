from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class UserPreferences:
    """Explicit preferences a user sets via the preferences page."""

    username: str = ""
    preferOnCampus: bool | None = None
    preferredVibe: str | None = None  # "library", "cafe", "outdoor", or None
    needsWifi: bool = False
    needsParking: bool = False
    needsOutlets: bool = False
    preferQuiet: bool = False
    maxDistanceMiles: float | None = None
    preferLateHours: bool = False

    def toDict(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "preferOnCampus": self.preferOnCampus,
            "preferredVibe": self.preferredVibe,
            "needsWifi": self.needsWifi,
            "needsParking": self.needsParking,
            "needsOutlets": self.needsOutlets,
            "preferQuiet": self.preferQuiet,
            "maxDistanceMiles": self.maxDistanceMiles,
            "preferLateHours": self.preferLateHours,
        }

    @classmethod
    def fromDict(cls, data: dict[str, Any]) -> UserPreferences:
        return cls(
            username=data.get("username", ""),
            preferOnCampus=data.get("preferOnCampus"),
            preferredVibe=data.get("preferredVibe"),
            needsWifi=bool(data.get("needsWifi", False)),
            needsParking=bool(data.get("needsParking", False)),
            needsOutlets=bool(data.get("needsOutlets", False)),
            preferQuiet=bool(data.get("preferQuiet", False)),
            maxDistanceMiles=data.get("maxDistanceMiles"),
            preferLateHours=bool(data.get("preferLateHours", False)),
        )


@dataclass
class RequestContext:
    """Per-request contextual signals that affect ranking."""

    timeOfDay: str | None = None  # "morning", "afternoon", "evening", "night"
    onCampusOnly: bool = False
    commuteMode: str | None = None  # "walking", "driving", "transit"
    query: str | None = None  # free-text search query

    @classmethod
    def fromDict(cls, data: dict[str, Any]) -> RequestContext:
        return cls(
            timeOfDay=data.get("timeOfDay"),
            onCampusOnly=bool(data.get("onCampusOnly", False)),
            commuteMode=data.get("commuteMode"),
            query=data.get("query"),
        )
