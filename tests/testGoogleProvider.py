import json
from unittest.mock import patch

from studySpotRecommender.appConfig import AppConfig
from studySpotRecommender.providers.googlePlaces import GooglePlacesProvider


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def testGoogleProviderReturnsEmptyWithoutKey() -> None:
    provider = GooglePlacesProvider(AppConfig(googleApiKey=None))
    assert provider.fetch() == []


def testGoogleProviderBuildsV1RequestAndParsesResponse() -> None:
    provider = GooglePlacesProvider(AppConfig(googleApiKey="test-key", maxResultsPerSource=5))
    payload = {
        "places": [
            {
                "id": "abc123",
                "displayName": {"text": "Science Library"},
                "formattedAddress": "Irvine, CA",
                "location": {"latitude": 33.64, "longitude": -117.84},
                "currentOpeningHours": {"weekdayDescriptions": ["Mon: 8-5"], "openNow": True},
                "parkingOptions": {"freeParkingLot": True},
                "accessibilityOptions": {"wheelchairAccessibleParking": True},
            }
        ]
    }

    captured: dict[str, object] = {}

    def _fakeUrlopen(req, timeout=0):
        captured["url"] = req.full_url
        captured["method"] = req.get_method()
        captured["headers"] = dict(req.header_items())
        captured["body"] = json.loads(req.data.decode("utf-8"))
        captured["timeout"] = timeout
        return _FakeResponse(payload)

    with patch("studySpotRecommender.providers.googlePlaces.urlopen", side_effect=_fakeUrlopen):
        records = provider.fetch()

    assert len(records) == 1
    assert records[0].name == "Science Library"
    assert captured["url"] == "https://places.googleapis.com/v1/places:searchNearby"
    assert captured["method"] == "POST"
    assert captured["headers"]["X-goog-api-key"] == "test-key"
    assert "places.id" in captured["headers"]["X-goog-fieldmask"]
    assert "cafe" in captured["body"]["includedTypes"]
