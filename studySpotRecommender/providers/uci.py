from __future__ import annotations

import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from studySpotRecommender.dataModels import SourceRecord
from .providerBase import BaseProvider


# Curated list of physical UCI study locations.
# Each entry produces exactly one SourceRecord.
# Add new physical study spaces here as they open.
_KNOWN_UCI_STUDY_SPOTS: tuple[dict, ...] = (
    {
        "name": "Langson Library",
        "url": "https://www.lib.uci.edu/langson",
    },
    {
        "name": "Science Library",
        "url": "https://www.lib.uci.edu/science",
    },
    {
        "name": "Gateway Study Center",
        "url": "https://www.lib.uci.edu/gateway-study-center",
    },
    {
        "name": "Multimedia Resources Center",
        "url": "https://www.lib.uci.edu/mrc",
    },
    {
        "name": "Grunigen Medical Library",
        "url": "https://www.lib.uci.edu/medical",
    },
)

# Shared values for all on-campus UCI library spots.
_ON_CAMPUS_PARKING = "permit-based campus parking"
_ON_CAMPUS_WIFI = "Campus WiFi expected"
_ON_CAMPUS_TRANSPORT = "Campus shuttle and OC transit nearby"
_UCI_ADDRESS = "University of California, Irvine"


class UCIProvider(BaseProvider):
    name = "uci"

    def _fetchHtml(self, url: str) -> str | None:
        req = Request(url, headers={"User-Agent": self.config.userAgent})
        try:
            with urlopen(req, timeout=self.config.requestTimeoutS) as response:
                return response.read().decode("utf-8", errors="ignore")
        except (HTTPError, URLError):
            return None

    @staticmethod
    def _extractHours(html: str) -> str | None:
        """Extract hours text from HTML only when found near a recognized hours label.

        The match must be anchored to a contextual keyword (hours, open, close) to
        avoid pulling in random time-like patterns from unrelated page content such as
        phone numbers, dates, or event listings.
        """
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text)

        # Pattern A: "Library Hours: Mon–Thu 8am–midnight" style
        weekday_match = re.search(
            r"(?:library\s+hours?|building\s+hours?|open(?:ing)?\s+hours?|hours?\s*:)"
            r"[^.\n]{0,40}?"
            r"((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[^.\n<]{5,80}?"
            r"\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))",
            text, re.I,
        )
        if weekday_match:
            return weekday_match.group(1).strip()

        # Pattern B: bare time range near "hours" keyword, e.g. "Hours: 8:00 AM – 10:00 PM"
        range_match = re.search(
            r"(?:hours?|open)\s*[:\-]?\s*"
            r"(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)"
            r"[^.\n<]{1,30}?"
            r"\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm))",
            text, re.I,
        )
        if range_match:
            return range_match.group(1).strip()

        return None

    def fetch(self) -> list[SourceRecord]:
        records: list[SourceRecord] = []

        for spot in _KNOWN_UCI_STUDY_SPOTS:
            html = self._fetchHtml(spot["url"])
            hoursText: str | None = self._extractHours(html) if html else None

            records.append(
                SourceRecord(
                    provider=self.name,
                    sourceId=spot["url"],
                    name=spot["name"],
                    latitude=self.config.uciLat,
                    longitude=self.config.uciLon,
                    address=_UCI_ADDRESS,
                    hoursText=hoursText,
                    parking=_ON_CAMPUS_PARKING,
                    wifi=_ON_CAMPUS_WIFI,
                    transportNotes=_ON_CAMPUS_TRANSPORT,
                    onCampus=True,
                    raw={"url": spot["url"]},
                )
            )

        return records
