from __future__ import annotations

import re
from urllib.error import URLError
from urllib.request import Request, urlopen

from studySpotRecommender.dataModels import SourceRecord
from .providerBase import BaseProvider


class UCIProvider(BaseProvider):
    name = "uci"

    studyUrls = [
        "https://www.lib.uci.edu/hours",
        "https://www.lib.uci.edu/study-on-campus",
        "https://parking.uci.edu/",
    ]

    def fetch(self) -> list[SourceRecord]:
        records: list[SourceRecord] = []
        for url in self.studyUrls:
            try:
                req = Request(url, headers={"User-Agent": self.config.userAgent})
                with urlopen(req, timeout=self.config.requestTimeoutS) as response:
                    html = response.read().decode("utf-8", errors="ignore")
            except URLError:
                continue

            titleMatch = re.search(r"<title>(.*?)</title>", html, flags=re.I | re.S)
            title = re.sub(r"\s+", " ", titleMatch.group(1)).strip() if titleMatch else "UCI Study Resource"
            textBlob = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
            hoursMatch = re.search(r"(\d{1,2}:?\d{0,2}\s?(AM|PM).{0,40}?\d{1,2}:?\d{0,2}\s?(AM|PM))", textBlob, re.I)
            parkingHint = "permit-based parking" if "permit" in textBlob.lower() else None
            chargingHint = "EV charging info available" if "charging" in textBlob.lower() else None

            records.append(
                SourceRecord(
                    provider=self.name,
                    sourceId=url,
                    name=title,
                    latitude=self.config.uciLat,
                    longitude=self.config.uciLon,
                    address="University of California, Irvine",
                    hoursText=hoursMatch.group(1) if hoursMatch else None,
                    parking=parkingHint,
                    charging=chargingHint,
                    wifi="Campus WiFi expected",
                    transportNotes="Campus shuttle and OC transit nearby",
                    onCampus=True,
                    raw={"url": url},
                )
            )
        return records
