from __future__ import annotations

import json
import os
import sqlite3
from contextlib import closing

from studySpotRecommender.dataModels import CanonicalStudySpot, SourceRecord


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
                    canonicalKey TEXT NOT NULL UNIQUE,
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
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sourceRecords (
                    provider TEXT NOT NULL,
                    sourceId TEXT NOT NULL,
                    fetchedAt TEXT NOT NULL,
                    name TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    address TEXT,
                    hoursText TEXT,
                    openNow INTEGER,
                    parking TEXT,
                    wifi TEXT,
                    charging TEXT,
                    transportNotes TEXT,
                    onCampus INTEGER NOT NULL,
                    raw TEXT NOT NULL,
                    PRIMARY KEY (provider, sourceId, fetchedAt)
                )
                """
            )
            self._runMigrations(conn)
            conn.commit()

    def _runMigrations(self, conn: sqlite3.Connection) -> None:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(canonicalSpots)")}
        if "canonicalKey" not in columns:
            conn.execute("ALTER TABLE canonicalSpots ADD COLUMN canonicalKey TEXT")
            conn.execute("UPDATE canonicalSpots SET canonicalKey = canonicalId WHERE canonicalKey IS NULL")
            conn.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_canonical_spots_canonical_key ON canonicalSpots(canonicalKey)"
            )

    def insertSourceRecords(self, records: list[SourceRecord]) -> None:
        with closing(sqlite3.connect(self.path)) as conn:
            conn.executemany(
                """
                INSERT OR IGNORE INTO sourceRecords (
                    provider, sourceId, fetchedAt, name, latitude, longitude, address,
                    hoursText, openNow, parking, wifi, charging, transportNotes, onCampus, raw
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        r.provider,
                        r.sourceId,
                        r.fetchedAt,
                        r.name,
                        r.latitude,
                        r.longitude,
                        r.address,
                        r.hoursText,
                        1 if r.openNow else 0 if r.openNow is not None else None,
                        r.parking,
                        r.wifi,
                        r.charging,
                        r.transportNotes,
                        1 if r.onCampus else 0,
                        json.dumps(r.raw),
                    )
                    for r in records
                ],
            )
            conn.commit()

    def upsertMany(self, spots: list[CanonicalStudySpot]) -> None:
        with closing(sqlite3.connect(self.path)) as conn:
            conn.executemany(
                """
                INSERT INTO canonicalSpots (
                    canonicalId, canonicalKey, name, latitude, longitude, address, onCampus,
                    sourceIds, features, featureProvenance, confidence, lastRefreshedAt
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(canonicalKey) DO UPDATE SET
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
                        s.canonicalKey,
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
