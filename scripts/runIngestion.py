#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from studySpotRecommender.appConfig import AppConfig
from studySpotRecommender.ingestionPipeline import IngestionPipeline


def parseArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run UCI study spot ingestion pipeline")
    parser.add_argument("--radiusMiles", type=float, default=5.0)
    parser.add_argument("--sqlitePath", type=str, default="data/studySpots.db")
    parser.add_argument("--maxResults", type=int, default=50)
    parser.add_argument(
        "--providers",
        type=str,
        default="",
        help="Comma-separated provider names (uci,osm,google,yelp,foursquare)",
    )
    parser.add_argument("--verbose", action="store_true", help="Print per-provider fetch diagnostics")
    parser.add_argument(
        "--printRecords",
        type=int,
        default=0,
        help="When verbose, print first N records per provider",
    )
    return parser.parse_args()


def main() -> None:
    args = parseArgs()
    providerNames = tuple(
        provider.strip().lower() for provider in args.providers.split(",") if provider.strip()
    )

    config = AppConfig(
        radiusMiles=args.radiusMiles,
        sqlitePath=args.sqlitePath,
        maxResultsPerSource=args.maxResults,
        enabledProviders=providerNames,
        verbose=args.verbose,
        printRecordsPerProvider=max(args.printRecords, 0),
    )
    pipeline = IngestionPipeline(config)
    result = pipeline.ingest()
    print(json.dumps(result.__dict__, indent=2))


if __name__ == "__main__":
    main()
