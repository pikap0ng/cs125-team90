#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from studySpotRecommender.server import createApp


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the study spot recommender API")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--db", type=str, default="data/studySpots.db")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    app = createApp(dbPath=args.db)
    print(f"Starting server on {args.host}:{args.port} with DB: {args.db}")
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
