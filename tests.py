from study_spot_recommender.Models import SourceRecord
from study_spot_recommender.Normalize import deduplicate


def test_deduplicate_merges_same_name_and_location() -> None:
    records = [
        SourceRecord(
            provider="a",
            source_id="1",
            name="Science Library",
            latitude=33.64,
            longitude=-117.84,
            wifi="yes",
        ),
        SourceRecord(
            provider="b",
            source_id="2",
            name="Science Library",
            latitude=33.64001,
            longitude=-117.84001,
            parking="garage",
        ),
    ]

    canonical = deduplicate(records, distance_threshold_m=100)

    assert len(canonical) == 1
    assert canonical[0].source_ids == {"a": "1", "b": "2"}
    assert canonical[0].features["wifi"] == "yes"
    assert canonical[0].features["parking"] == "garage"
