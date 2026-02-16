from urllib.error import HTTPError
from unittest.mock import patch

from studySpotRecommender.appConfig import AppConfig
from studySpotRecommender.providers.uci import UCIProvider


class _FakeResponse:
    def __init__(self, body: str):
        self._body = body

    def read(self) -> bytes:
        return self._body.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def testUciProviderCrawlsDiscoveredLinksAndFiltersNonStudyPages() -> None:
    provider = UCIProvider(AppConfig(maxResultsPerSource=10))

    pages = {
        "https://www.lib.uci.edu/study-space-locator": """
            <html><head><title>Study Space Locator</title></head>
            <body>
              <a href='https://www.lib.uci.edu/gateway-study-center'>Gateway</a>
              <a href='https://www.lib.uci.edu/contact-us'>Contact</a>
            </body></html>
        """,
        "https://www.lib.uci.edu/gateway-study-center": """
            <html><head><title>Gateway Study Center</title></head>
            <body>Open 8:00 AM - 10:00 PM, WiFi available.</body></html>
        """,
        "https://www.lib.uci.edu/contact-us": """
            <html><head><title>Contact</title></head>
            <body>Office directory only.</body></html>
        """,
    }

    def _fakeUrlopen(req, timeout=0):
        url = provider._canonicalizeUrl(req.full_url)
        if url in pages:
            return _FakeResponse(pages[url])
        raise HTTPError(req.full_url, 404, "Not Found", hdrs=None, fp=None)

    with patch("studySpotRecommender.providers.uci.urlopen", side_effect=_fakeUrlopen):
        records = provider.fetch()

    source_ids = {record.sourceId for record in records}
    assert "https://www.lib.uci.edu/study-space-locator" in source_ids
    assert "https://www.lib.uci.edu/gateway-study-center" in source_ids
    assert "https://www.lib.uci.edu/contact-us" not in source_ids
    assert all(record.onCampus for record in records)
