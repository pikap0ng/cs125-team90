#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from study_spot_recommender.Config import AppConfig
from study_spot_recommender.Pipeline import IngestionPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run UCI study spot ingestion pipeline")
    parser.add_argument("--radius-miles", type=float, default=5.0)
    parser.add_argument("--sqlite-path", type=str, default="data/study_spots.db")
    parser.add_argument("--max-results", type=int, default=50)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = AppConfig(
        radius_miles=args.radius_miles,
        sqlite_path=args.sqlite_path,
        max_results_per_source=args.max_results,
    )
    pipeline = IngestionPipeline(config)
    result = pipeline.ingest()
    print(json.dumps(result.__dict__, indent=2))


if __name__ == "__main__":
    main()
