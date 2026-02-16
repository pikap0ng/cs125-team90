from __future__ import annotations

import re
from collections import deque
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen

from studySpotRecommender.dataModels import SourceRecord
from .providerBase import BaseProvider


class UCIProvider(BaseProvider):
    name = "uci"

    seedUrls = (
        "https://www.lib.uci.edu/study-space-locator",
        "https://www.lib.uci.edu/hours",
        "https://www.lib.uci.edu/gateway-study-center",
        "https://www.lib.uci.edu/langson",
        "https://www.lib.uci.edu/science",
        "https://www.lib.uci.edu/mrc",
        "https://www.lib.uci.edu/locations-directions-parking",
        "https://spaces.lib.uci.edu/appointments",
        "https://parking.uci.edu/",
    )
    allowedDomains = ("uci.edu",)
    discoveryKeywords = (
        "study",
        "library",
        "langson",
        "science",
        "gateway",
        "learning",
        "reserve",
        "hours",
        "parking",
        "commons",
        "space",
        "mrc",
    )

    def _fetchHtml(self, url: str) -> str | None:
        req = Request(url, headers={"User-Agent": self.config.userAgent})
        try:
            with urlopen(req, timeout=self.config.requestTimeoutS) as response:
                return response.read().decode("utf-8", errors="ignore")
        except (HTTPError, URLError):
            return None

    def _canonicalizeUrl(self, url: str) -> str:
        parsed = urlparse(url)
        normalizedPath = parsed.path.rstrip("/") or "/"
        return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), normalizedPath, "", "", ""))

    def _isAllowedUciUrl(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme not in {"https", "http"}:
            return False
        host = parsed.netloc.lower()
        return any(host.endswith(domain) for domain in self.allowedDomains)

    def _extractLinks(self, sourceUrl: str, html: str) -> list[str]:
        links: list[str] = []
        for match in re.finditer(r'href=["\']([^"\']+)["\']', html, flags=re.I):
            absolute = urljoin(sourceUrl, match.group(1).strip())
            if not self._isAllowedUciUrl(absolute):
                continue
            canonical = self._canonicalizeUrl(absolute)
            text = canonical.lower()
            if any(keyword in text for keyword in self.discoveryKeywords):
                links.append(canonical)
        return links

    def _looksLikeStudyResource(self, url: str, title: str, textBlob: str) -> bool:
        haystack = f"{url} {title} {textBlob}".lower()
        return any(keyword in haystack for keyword in self.discoveryKeywords)

    def fetch(self) -> list[SourceRecord]:
        records: list[SourceRecord] = []
        seenUrls: set[str] = set()
        queue = deque(self._canonicalizeUrl(url) for url in self.seedUrls)

        maxRecords = max(self.config.maxResultsPerSource, 1)
        maxPagesToScan = max(maxRecords * 4, 40)
        scannedPages = 0

        while queue and len(records) < maxRecords and scannedPages < maxPagesToScan:
            url = queue.popleft()
            if url in seenUrls:
                continue
            seenUrls.add(url)

            html = self._fetchHtml(url)
            scannedPages += 1
            if not html:
                continue

            for discoveredUrl in self._extractLinks(url, html):
                if discoveredUrl not in seenUrls:
                    queue.append(discoveredUrl)

            titleMatch = re.search(r"<title>(.*?)</title>", html, flags=re.I | re.S)
            title = re.sub(r"\s+", " ", titleMatch.group(1)).strip() if titleMatch else "UCI Study Resource"
            textBlob = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))

            if not self._looksLikeStudyResource(url, title, textBlob):
                continue

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
                    raw={"url": url, "scannedPages": scannedPages},
                )
            )

        return records
