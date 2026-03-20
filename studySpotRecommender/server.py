
from __future__ import annotations

import json
from typing import Any

from flask import Flask, jsonify, request

from studySpotRecommender.ranker import rankSpots
from studySpotRecommender.storage.sqliteRepo import SQLiteRepository
from studySpotRecommender.userModel import RequestContext, UserPreferences


def createApp(dbPath: str = "data/studySpots.db") -> Flask:
    app = Flask(__name__)
    repo = SQLiteRepository(dbPath)
    repo.initialize()

    # ── health ──

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    # ── preferences ──

    @app.route("/save_preferences", methods=["POST"])
    def savePreferences():
        body = request.get_json(silent=True) or {}
        username = body.get("username", "").strip()
        if not username:
            return jsonify({"error": "username is required"}), 400

        repo.saveUserPreferences(username, body)
        return jsonify({"status": "saved", "username": username})

    @app.route("/preferences/<username>", methods=["GET"])
    def getPreferences(username: str):
        prefs = repo.getUserPreferences(username)
        if prefs is None:
            return jsonify({"error": "no preferences found", "username": username}), 404
        return jsonify(prefs)


    @app.route("/recommendations", methods=["POST"])
    def recommendations():
        body = request.get_json(silent=True) or {}
        username = body.get("username", "").strip()

        # Load saved preferences or use what was sent in the request
        savedPrefs = repo.getUserPreferences(username) if username else None
        prefData = savedPrefs if savedPrefs else body.get("preferences", {})
        prefs = UserPreferences.fromDict(prefData)

        # Parse context
        context = RequestContext.fromDict(body.get("context", {}))

        # Load bookmarks
        bookmarkedKeys = repo.getBookmarkedKeys(username) if username else set()

        # Load all spots and rank
        allSpots = repo.getAllCanonicalSpots()
        topK = body.get("topK", 10)
        results = rankSpots(allSpots, prefs, context, bookmarkedKeys, topK=topK)

        return jsonify({
            "username": username,
            "totalCandidates": len(allSpots),
            "resultsReturned": len(results),
            "results": [
                {
                    "canonicalId": r.canonicalId,
                    "canonicalKey": r.canonicalKey,
                    "name": r.name,
                    "latitude": r.latitude,
                    "longitude": r.longitude,
                    "address": r.address,
                    "onCampus": r.onCampus,
                    "features": r.features,
                    "score": r.score,
                    "explanation": r.explanation,
                    "distanceMiles": r.distanceMiles,
                }
                for r in results
            ],
        })

    # ── spot details ──

    @app.route("/spots/<spotId>", methods=["GET"])
    def spotDetails(spotId: str):
        spot = repo.getSpotById(spotId)
        if spot is None:
            spot = repo.getSpotByKey(spotId)
        if spot is None:
            return jsonify({"error": "spot not found"}), 404

        # Parse JSON string fields for the response
        for field in ("features", "featureProvenance", "confidence", "sourceIds"):
            if isinstance(spot.get(field), str):
                spot[field] = json.loads(spot[field])

        return jsonify(spot)



    @app.route("/bookmarks", methods=["POST"])
    def addBookmark():
        body = request.get_json(silent=True) or {}
        username = body.get("username", "").strip()
        canonicalKey = body.get("canonicalKey", "").strip()
        if not username or not canonicalKey:
            return jsonify({"error": "username and canonicalKey are required"}), 400
        repo.addBookmark(username, canonicalKey)
        return jsonify({"status": "bookmarked", "username": username, "canonicalKey": canonicalKey})

    @app.route("/bookmarks", methods=["DELETE"])
    def removeBookmark():
        body = request.get_json(silent=True) or {}
        username = body.get("username", "").strip()
        canonicalKey = body.get("canonicalKey", "").strip()
        if not username or not canonicalKey:
            return jsonify({"error": "username and canonicalKey are required"}), 400
        repo.removeBookmark(username, canonicalKey)
        return jsonify({"status": "removed", "username": username, "canonicalKey": canonicalKey})

    @app.route("/bookmarks/<username>", methods=["GET"])
    def listBookmarks(username: str):
        keys = repo.getBookmarkedKeys(username)
        return jsonify({"username": username, "bookmarks": sorted(keys)})

    return app
