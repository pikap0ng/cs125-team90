import json
import sqlite3

from studySpotRecommender.dataModels import CanonicalStudySpot, SourceRecord, buildCanonicalKey
from studySpotRecommender.storage.sqliteRepo import SQLiteRepository


def _spot(name: str, lat: float, lon: float, source: str, source_id: str) -> CanonicalStudySpot:
    record = SourceRecord(provider=source, sourceId=source_id, name=name, latitude=lat, longitude=lon)
    return CanonicalStudySpot.fromSource(record)


def testCanonicalKeyIsDeterministic() -> None:
    key_a = buildCanonicalKey("The Starbucks Cafe", 33.64051, -117.84429)
    key_b = buildCanonicalKey("Starbucks", 33.64050, -117.84431)
    assert key_a == key_b


def testUpsertUsesCanonicalKeyAcrossRuns(tmp_path) -> None:
    db_path = tmp_path / "spots.db"
    repo = SQLiteRepository(str(db_path))
    repo.initialize()

    first = _spot("Science Library", 33.64, -117.84, "uci", "1")
    second = _spot("Science Library", 33.64001, -117.84002, "google", "2")

    assert first.canonicalKey == second.canonicalKey

    repo.upsertMany([first])
    repo.upsertMany([second])

    conn = sqlite3.connect(db_path)
    row_count = conn.execute("SELECT COUNT(*) FROM canonicalSpots").fetchone()[0]
    source_ids = conn.execute("SELECT sourceIds FROM canonicalSpots").fetchone()[0]
    conn.close()

    assert row_count == 1
    assert json.loads(source_ids) == {"google": "2"}


def testSourceRecordsArePersisted(tmp_path) -> None:
    db_path = tmp_path / "spots.db"
    repo = SQLiteRepository(str(db_path))
    repo.initialize()

    records = [
        SourceRecord(provider="uci", sourceId="abc", name="Library", latitude=1.0, longitude=2.0),
        SourceRecord(provider="uci", sourceId="abc", name="Library", latitude=1.0, longitude=2.0),
    ]
    repo.insertSourceRecords(records)

    conn = sqlite3.connect(db_path)
    row_count = conn.execute("SELECT COUNT(*) FROM sourceRecords").fetchone()[0]
    conn.close()

    assert row_count == 2
