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


def testDeduplicateDoesNotMergeFarApartPlaces() -> None:
    records = [
        SourceRecord(
            provider="a",
            sourceId="1",
            name="Starbucks",
            latitude=33.64,
            longitude=-117.84,
        ),
        SourceRecord(
            provider="b",
            sourceId="2",
            name="Starbucks",
            latitude=33.68,
            longitude=-117.90,
        ),
    ]

    canonical = deduplicate(records, distanceThresholdM=100)

    assert len(canonical) == 2


def testDeduplicateMergesFuzzyNameCloseBy() -> None:
    records = [
        SourceRecord(
            provider="a",
            sourceId="1",
            name="Starbucks UCI",
            latitude=33.6405,
            longitude=-117.8443,
        ),
        SourceRecord(
            provider="b",
            sourceId="2",
            name="Starbucks",
            latitude=33.64052,
            longitude=-117.84431,
        ),
    ]

    canonical = deduplicate(records, distanceThresholdM=100)

    assert len(canonical) == 1


def testDeduplicatePrefersFirstProviderWhenValuesConflict() -> None:
    records = [
        SourceRecord(
            provider="google",
            sourceId="g-1",
            name="Gateway Study Center",
            latitude=33.6405,
            longitude=-117.8443,
            parking="garage",
            wifi="wlan",
        ),
        SourceRecord(
            provider="osm",
            sourceId="o-1",
            name="Gateway Study Center",
            latitude=33.64051,
            longitude=-117.84431,
            parking="street",
            wifi="no",
        ),
    ]

    canonical = deduplicate(records, distanceThresholdM=100)

    assert len(canonical) == 1
    assert canonical[0].sourceIds == {"google": "g-1", "osm": "o-1"}
    assert canonical[0].features["parking"] == "garage"
    assert canonical[0].features["wifi"] == "wlan"


def testDeduplicatePrecedenceChangesWhenProviderOrderChanges() -> None:
    records = [
        SourceRecord(
            provider="osm",
            sourceId="o-1",
            name="Gateway Study Center",
            latitude=33.64051,
            longitude=-117.84431,
            parking="street",
            wifi="no",
        ),
        SourceRecord(
            provider="google",
            sourceId="g-1",
            name="Gateway Study Center",
            latitude=33.6405,
            longitude=-117.8443,
            parking="garage",
            wifi="wlan",
        ),
    ]

    canonical = deduplicate(records, distanceThresholdM=100)

    assert len(canonical) == 1
    assert canonical[0].features["parking"] == "street"
    assert canonical[0].features["wifi"] == "no"


def testDeduplicateAllowsFalseToFillMissingBooleanFeature() -> None:
    records = [
        SourceRecord(
            provider="google",
            sourceId="g-1",
            name="Gateway Study Center",
            latitude=33.6405,
            longitude=-117.8443,
            openNow=None,
        ),
        SourceRecord(
            provider="osm",
            sourceId="o-1",
            name="Gateway Study Center",
            latitude=33.64051,
            longitude=-117.84431,
            openNow=False,
        ),
    ]

    canonical = deduplicate(records, distanceThresholdM=100)

    assert len(canonical) == 1
    assert canonical[0].features["openNow"] is False
