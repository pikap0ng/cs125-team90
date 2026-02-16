from __future__ import annotations

import json
import os
import sqlite3
from contextlib import closing

from study_spot_recommender.Models import CanonicalStudySpot


class SQLiteRepository:
    def __init__(self, path: str):
        self.path = path

    def initialize(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with closing(sqlite3.connect(self.path)) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS canonical_spots (
                    canonical_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    address TEXT,
                    on_campus INTEGER NOT NULL,
                    source_ids TEXT NOT NULL,
                    features TEXT NOT NULL,
                    feature_provenance TEXT NOT NULL,
                    confidence TEXT NOT NULL,
                    last_refreshed_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def upsert_many(self, spots: list[CanonicalStudySpot]) -> None:
        with closing(sqlite3.connect(self.path)) as conn:
            conn.executemany(
                """
                INSERT INTO canonical_spots (
                    canonical_id, name, latitude, longitude, address, on_campus,
                    source_ids, features, feature_provenance, confidence, last_refreshed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(canonical_id) DO UPDATE SET
                    name=excluded.name,
                    latitude=excluded.latitude,
                    longitude=excluded.longitude,
                    address=excluded.address,
                    on_campus=excluded.on_campus,
                    source_ids=excluded.source_ids,
                    features=excluded.features,
                    feature_provenance=excluded.feature_provenance,
                    confidence=excluded.confidence,
                    last_refreshed_at=excluded.last_refreshed_at
                """,
                [
                    (
                        s.canonical_id,
                        s.name,
                        s.latitude,
                        s.longitude,
                        s.address,
                        1 if s.on_campus else 0,
                        json.dumps(s.source_ids),
                        json.dumps(s.features),
                        json.dumps(s.feature_provenance),
                        json.dumps(s.confidence),
                        s.last_refreshed_at,
                    )
                    for s in spots
                ],
            )
            conn.commit()
