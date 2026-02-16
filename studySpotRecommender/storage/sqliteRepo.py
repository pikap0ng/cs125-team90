from __future__ import annotations

import json
import os
import sqlite3
from contextlib import closing

from studySpotRecommender.dataModels import CanonicalStudySpot


class SQLiteRepository:
    def __init__(self, path: str):
        self.path = path

    def initialize(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with closing(sqlite3.connect(self.path)) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS canonicalSpots (
                    canonicalId TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    address TEXT,
                    onCampus INTEGER NOT NULL,
                    sourceIds TEXT NOT NULL,
                    features TEXT NOT NULL,
                    featureProvenance TEXT NOT NULL,
                    confidence TEXT NOT NULL,
                    lastRefreshedAt TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def upsertMany(self, spots: list[CanonicalStudySpot]) -> None:
        with closing(sqlite3.connect(self.path)) as conn:
            conn.executemany(
                """
                INSERT INTO canonicalSpots (
                    canonicalId, name, latitude, longitude, address, onCampus,
                    sourceIds, features, featureProvenance, confidence, lastRefreshedAt
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(canonicalId) DO UPDATE SET
                    name=excluded.name,
                    latitude=excluded.latitude,
                    longitude=excluded.longitude,
                    address=excluded.address,
                    onCampus=excluded.onCampus,
                    sourceIds=excluded.sourceIds,
                    features=excluded.features,
                    featureProvenance=excluded.featureProvenance,
                    confidence=excluded.confidence,
                    lastRefreshedAt=excluded.lastRefreshedAt
                """,
                [
                    (
                        s.canonicalId,
                        s.name,
                        s.latitude,
                        s.longitude,
                        s.address,
                        1 if s.onCampus else 0,
                        json.dumps(s.sourceIds),
                        json.dumps(s.features),
                        json.dumps(s.featureProvenance),
                        json.dumps(s.confidence),
                        s.lastRefreshedAt,
                    )
                    for s in spots
                ],
            )
            conn.commit()
