from __future__ import annotations

import json
import os
import sqlite3
from contextlib import closing
from typing import Any

from studySpotRecommender.dataModels import CanonicalStudySpot, SourceRecord


class SQLiteRepository:
    def __init__(self, path: str):
        self.path = path

    def initialize(self) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
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
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS userPreferences (
                    username TEXT PRIMARY KEY,
                    preferOnCampus INTEGER,
                    preferredVibe TEXT,
                    needsWifi INTEGER NOT NULL DEFAULT 0,
                    needsParking INTEGER NOT NULL DEFAULT 0,
                    needsOutlets INTEGER NOT NULL DEFAULT 0,
                    preferQuiet INTEGER NOT NULL DEFAULT 0,
                    maxDistanceMiles REAL,
                    preferLateHours INTEGER NOT NULL DEFAULT 0,
                    updatedAt TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS userBookmarks (
                    username TEXT NOT NULL,
                    canonicalKey TEXT NOT NULL,
                    createdAt TEXT NOT NULL,
                    PRIMARY KEY (username, canonicalKey)
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

    # ── source records ──

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

    # ── canonical spots ──

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

    def getAllCanonicalSpots(self) -> list[dict[str, Any]]:
        """Return all canonical spots as a list of dicts."""
        with closing(sqlite3.connect(self.path)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM canonicalSpots").fetchall()
            return [dict(row) for row in rows]

    def getSpotByKey(self, canonicalKey: str) -> dict[str, Any] | None:
        with closing(sqlite3.connect(self.path)) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM canonicalSpots WHERE canonicalKey = ?", (canonicalKey,)
            ).fetchone()
            return dict(row) if row else None

    def getSpotById(self, canonicalId: str) -> dict[str, Any] | None:
        with closing(sqlite3.connect(self.path)) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM canonicalSpots WHERE canonicalId = ?", (canonicalId,)
            ).fetchone()
            return dict(row) if row else None

    # ── user preferences ──

    def saveUserPreferences(self, username: str, prefs: dict[str, Any]) -> None:
        from datetime import datetime, timezone

        now = datetime.now(tz=timezone.utc).isoformat()
        with closing(sqlite3.connect(self.path)) as conn:
            conn.execute(
                """
                INSERT INTO userPreferences (
                    username, preferOnCampus, preferredVibe, needsWifi, needsParking,
                    needsOutlets, preferQuiet, maxDistanceMiles, preferLateHours, updatedAt
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(username) DO UPDATE SET
                    preferOnCampus=excluded.preferOnCampus,
                    preferredVibe=excluded.preferredVibe,
                    needsWifi=excluded.needsWifi,
                    needsParking=excluded.needsParking,
                    needsOutlets=excluded.needsOutlets,
                    preferQuiet=excluded.preferQuiet,
                    maxDistanceMiles=excluded.maxDistanceMiles,
                    preferLateHours=excluded.preferLateHours,
                    updatedAt=excluded.updatedAt
                """,
                (
                    username,
                    1 if prefs.get("preferOnCampus") is True else (0 if prefs.get("preferOnCampus") is False else None),
                    prefs.get("preferredVibe"),
                    1 if prefs.get("needsWifi") else 0,
                    1 if prefs.get("needsParking") else 0,
                    1 if prefs.get("needsOutlets") else 0,
                    1 if prefs.get("preferQuiet") else 0,
                    prefs.get("maxDistanceMiles"),
                    1 if prefs.get("preferLateHours") else 0,
                    now,
                ),
            )
            conn.commit()

    def getUserPreferences(self, username: str) -> dict[str, Any] | None:
        with closing(sqlite3.connect(self.path)) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM userPreferences WHERE username = ?", (username,)
            ).fetchone()
            if not row:
                return None
            d = dict(row)
            campus = d.get("preferOnCampus")
            d["preferOnCampus"] = True if campus == 1 else (False if campus == 0 else None)
            for boolField in ("needsWifi", "needsParking", "needsOutlets", "preferQuiet", "preferLateHours"):
                d[boolField] = bool(d.get(boolField))
            return d

    # ── bookmarks ──

    def addBookmark(self, username: str, canonicalKey: str) -> None:
        from datetime import datetime, timezone

        now = datetime.now(tz=timezone.utc).isoformat()
        with closing(sqlite3.connect(self.path)) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO userBookmarks (username, canonicalKey, createdAt) VALUES (?, ?, ?)",
                (username, canonicalKey, now),
            )
            conn.commit()

    def removeBookmark(self, username: str, canonicalKey: str) -> None:
        with closing(sqlite3.connect(self.path)) as conn:
            conn.execute(
                "DELETE FROM userBookmarks WHERE username = ? AND canonicalKey = ?",
                (username, canonicalKey),
            )
            conn.commit()

    def getBookmarkedKeys(self, username: str) -> set[str]:
        with closing(sqlite3.connect(self.path)) as conn:
            rows = conn.execute(
                "SELECT canonicalKey FROM userBookmarks WHERE username = ?", (username,)
            ).fetchall()
            return {row[0] for row in rows}
