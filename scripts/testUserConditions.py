#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from studySpotRecommender.appConfig import AppConfig
from studySpotRecommender.ingestionPipeline import IngestionPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run user-condition checks against UCI, OSM, and Google providers."
    )
    parser.add_argument("--sqlitePath", default="data/tmp_user_conditions.db")
    parser.add_argument("--radiusMiles", type=float, default=5.0)
    parser.add_argument("--maxResults", type=int, default=50)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def _count(conn: sqlite3.Connection, query: str) -> int:
    return int(conn.execute(query).fetchone()[0])


def main() -> None:
    args = parse_args()

    config = AppConfig(
        sqlitePath=args.sqlitePath,
        radiusMiles=args.radiusMiles,
        maxResultsPerSource=args.maxResults,
        enabledProviders=("uci", "osm", "google"),
        verbose=args.verbose,
    )
    pipeline = IngestionPipeline(config)
    result = pipeline.ingest()

    db_path = Path(args.sqlitePath)
    conn = sqlite3.connect(db_path)

    metrics = {
        "providersRequested": ["uci", "osm", "google"],
        "providersReturned": [
            row[0]
            for row in conn.execute(
                "SELECT DISTINCT provider FROM sourceRecords ORDER BY provider"
            )
        ],
        "sourceRecords": _count(conn, "SELECT COUNT(*) FROM sourceRecords"),
        "canonicalSpots": _count(conn, "SELECT COUNT(*) FROM canonicalSpots"),
        "cafeLikeNames": _count(
            conn,
            "SELECT COUNT(*) FROM canonicalSpots WHERE lower(name) LIKE '%cafe%' OR lower(name) LIKE '%coffee%'",
        ),
        "libraryLikeNames": _count(
            conn,
            "SELECT COUNT(*) FROM canonicalSpots WHERE lower(name) LIKE '%library%'",
        ),
        "onCampusSpots": _count(conn, "SELECT COUNT(*) FROM canonicalSpots WHERE onCampus = 1"),
        "wifiKnown": _count(
            conn,
            "SELECT COUNT(*) FROM canonicalSpots WHERE json_extract(features, '$.wifi') IS NOT NULL AND trim(json_extract(features, '$.wifi')) <> ''",
        ),
        "parkingKnown": _count(
            conn,
            "SELECT COUNT(*) FROM canonicalSpots WHERE json_extract(features, '$.parking') IS NOT NULL AND trim(json_extract(features, '$.parking')) <> ''",
        ),
        "chargingKnown": _count(
            conn,
            "SELECT COUNT(*) FROM canonicalSpots WHERE json_extract(features, '$.charging') IS NOT NULL AND trim(json_extract(features, '$.charging')) <> ''",
        ),
        "openNowTrue": _count(
            conn,
            "SELECT COUNT(*) FROM canonicalSpots WHERE json_extract(features, '$.openNow') = 1",
        ),
    }

    conn.close()

    print("Ingestion result:")
    print(json.dumps(result.__dict__, indent=2))
    print("\nScenario metrics:")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
