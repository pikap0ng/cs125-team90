import json
from unittest.mock import patch

from studySpotRecommender.appConfig import AppConfig
from studySpotRecommender.providers.osm import OSMProvider


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def testOverpassPayloadParsesNodeAndWay() -> None:
    payload = {
        "elements": [
            {
                "type": "node",
                "id": 1,
                "lat": 33.64,
                "lon": -117.84,
                "tags": {"name": "Node Cafe", "amenity": "cafe", "opening_hours": "Mo-Fr 08:00-17:00"},
            },
            {
                "type": "way",
                "id": 2,
                "center": {"lat": 33.65, "lon": -117.85},
                "tags": {"amenity": "library", "internet_access": "wlan"},
            },
        ]
    }
    provider = OSMProvider(AppConfig(maxResultsPerSource=10))

    with patch("studySpotRecommender.providers.osm.urlopen", return_value=_FakeResponse(payload)):
        records = provider.fetch()

    assert len(records) == 2
    assert records[0].name == "Node Cafe"
    assert records[0].sourceId == "node:1"
    assert records[1].name == "Library 2"
    assert records[1].wifi == "wlan"
