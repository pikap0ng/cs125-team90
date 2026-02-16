from __future__ import annotations

from dataclasses import dataclass

from studySpotRecommender.appConfig import AppConfig
from studySpotRecommender.dataModels import CanonicalStudySpot, SourceRecord
from studySpotRecommender.normalizer import deduplicate
from studySpotRecommender.providers import (
    FoursquareProvider,
    GooglePlacesProvider,
    OSMProvider,
    UCIProvider,
    YelpProvider,
)
from studySpotRecommender.storage.sqliteRepo import SQLiteRepository


@dataclass
class IngestionResult:
    totalSourceRecords: int
    totalCanonicalSpots: int
    storedAt: str


class IngestionPipeline:
    def __init__(self, config: AppConfig):
        self.config = config
        self.providers = [
            UCIProvider(config),
            GooglePlacesProvider(config),
            YelpProvider(config),
            FoursquareProvider(config),
            OSMProvider(config),
        ]
        self.repo = SQLiteRepository(config.sqlitePath)

    def collect(self) -> list[SourceRecord]:
        allRecords: list[SourceRecord] = []
        for provider in self.providers:
            records = provider.fetch()
            allRecords.extend(records)
        return allRecords

    def ingest(self) -> IngestionResult:
        self.repo.initialize()
        records = self.collect()
        self.repo.insertSourceRecords(records)
        canonicalSpots: list[CanonicalStudySpot] = deduplicate(records)
        self.repo.upsertMany(canonicalSpots)
        return IngestionResult(
            totalSourceRecords=len(records),
            totalCanonicalSpots=len(canonicalSpots),
            storedAt=self.config.sqlitePath,
        )
