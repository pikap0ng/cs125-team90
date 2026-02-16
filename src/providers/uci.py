from __future__ import annotations

import re
from urllib.error import URLError
from urllib.request import Request, urlopen

from study_spot_recommender.Models import SourceRecord
from .Base import BaseProvider


class UCIProvider(BaseProvider):
    name = "uci"

    STUDY_URLS = [
        "https://www.lib.uci.edu/hours",
        "https://www.lib.uci.edu/study-on-campus",
        "https://parking.uci.edu/",
    ]

    def fetch(self) -> list[SourceRecord]:
        records: list[SourceRecord] = []
        for url in self.STUDY_URLS:
            try:
                req = Request(url, headers={"User-Agent": self.config.user_agent})
                with urlopen(req, timeout=self.config.request_timeout_s) as response:
                    html = response.read().decode("utf-8", errors="ignore")
            except URLError:
                continue

            title_match = re.search(r"<title>(.*?)</title>", html, flags=re.I | re.S)
            title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else "UCI Study Resource"
            text_blob = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
            hours_match = re.search(r"(\d{1,2}:?\d{0,2}\s?(AM|PM).{0,40}?\d{1,2}:?\d{0,2}\s?(AM|PM))", text_blob, re.I)
            parking_hint = "permit-based parking" if "permit" in text_blob.lower() else None
            charging_hint = "EV charging info available" if "charging" in text_blob.lower() else None

            records.append(
                SourceRecord(
                    provider=self.name,
                    source_id=url,
                    name=title,
                    latitude=self.config.uci_lat,
                    longitude=self.config.uci_lon,
                    address="University of California, Irvine",
                    hours_text=hours_match.group(1) if hours_match else None,
                    parking=parking_hint,
                    charging=charging_hint,
                    wifi="Campus Wi-Fi expected",
                    transport_notes="Campus shuttle and OC transit nearby",
                    on_campus=True,
                    raw={"url": url},
                )
            )
        return records
