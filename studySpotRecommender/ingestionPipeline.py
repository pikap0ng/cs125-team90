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
        allProviders = [
            UCIProvider(config),
            GooglePlacesProvider(config),
            YelpProvider(config),
            FoursquareProvider(config),
            OSMProvider(config),
        ]
        enabled = {name.lower() for name in config.enabledProviders}
        self.providers = [p for p in allProviders if not enabled or p.name.lower() in enabled]
        self.repo = SQLiteRepository(config.sqlitePath)

    def collect(self) -> list[SourceRecord]:
        allRecords: list[SourceRecord] = []
        for provider in self.providers:
            if self.config.verbose:
                print(f"[provider] {provider.name}: starting fetch")
            try:
                records = provider.fetch()
            except Exception as err:
                if self.config.verbose:
                    print(f"[provider] {provider.name}: ERROR {err}")
                records = []
            if self.config.verbose:
                print(f"[provider] {provider.name}: fetched {len(records)} records")
                for record in records[: self.config.printRecordsPerProvider]:
                    print(
                        f"[record] {provider.name} | {record.name} | "
                        f"{record.latitude:.5f},{record.longitude:.5f} | {record.address or 'n/a'}"
                    )
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
