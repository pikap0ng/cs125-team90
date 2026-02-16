from __future__ import annotations

from dataclasses import dataclass

from study_spot_recommender.Config import AppConfig
from study_spot_recommender.Models import CanonicalStudySpot, SourceRecord
from study_spot_recommender.Normalize import deduplicate
from study_spot_recommender.providers import (
    FoursquareProvider,
    GooglePlacesProvider,
    OSMProvider,
    UCIProvider,
    YelpProvider,
)
from study_spot_recommender.storage.SqliteRepo import SQLiteRepository


@dataclass
class IngestionResult:
    total_source_records: int
    total_canonical_spots: int
    stored_at: str


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
        self.repo = SQLiteRepository(config.sqlite_path)

    def collect(self) -> list[SourceRecord]:
        all_records: list[SourceRecord] = []
        for provider in self.providers:
            records = provider.fetch()
            all_records.extend(records)
        return all_records

    def ingest(self) -> IngestionResult:
        self.repo.initialize()
        records = self.collect()
        canonical_spots: list[CanonicalStudySpot] = deduplicate(records)
        self.repo.upsert_many(canonical_spots)
        return IngestionResult(
            total_source_records=len(records),
            total_canonical_spots=len(canonical_spots),
            stored_at=self.config.sqlite_path,
        )
