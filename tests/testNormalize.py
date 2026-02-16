from studySpotRecommender.dataModels import SourceRecord
from studySpotRecommender.normalizer import deduplicate


def testDeduplicateMergesSameNameAndLocation() -> None:
    records = [
        SourceRecord(
            provider="a",
            sourceId="1",
            name="Science Library",
            latitude=33.64,
            longitude=-117.84,
            wifi="yes",
        ),
        SourceRecord(
            provider="b",
            sourceId="2",
            name="Science Library",
            latitude=33.64001,
            longitude=-117.84001,
            parking="garage",
        ),
    ]

    canonical = deduplicate(records, distanceThresholdM=100)

    assert len(canonical) == 1
    assert canonical[0].sourceIds == {"a": "1", "b": "2"}
    assert canonical[0].features["wifi"] == "yes"
    assert canonical[0].features["parking"] == "garage"
