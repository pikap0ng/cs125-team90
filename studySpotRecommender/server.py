from __future__ import annotations

import json
from typing import Any

from flask import Flask, jsonify, request

try:
    from flask_cors import CORS
except ImportError:
    CORS = None

from studySpotRecommender.ranker import rankSpots
from studySpotRecommender.storage.sqliteRepo import SQLiteRepository
from studySpotRecommender.userModel import RequestContext, UserPreferences


def _translateFlutterPrefs(body: dict[str, Any]) -> dict[str, Any]:
    if "preferOnCampus" in body or "needsWifi" in body or "preferredVibe" in body:
        return body

    amenities = body.get("amenities", {})
    locationType = body.get("location_type", {})

    onCampusVal = amenities.get("On Campus", 0)
    preferOnCampus = True if onCampusVal == 1 else (False if onCampusVal == -1 else None)

    preferredVibe = None
    for vibe, val in locationType.items():
        if val == 1:
            preferredVibe = vibe.lower()
            break

    maxDist = body.get("max_distance")
    if maxDist is not None and maxDist < 0:
        maxDist = None

    return {
        "username": body.get("username", ""),
        "preferOnCampus": preferOnCampus,
        "preferredVibe": preferredVibe,
        "needsWifi": False,
        "needsParking": False,
        "needsOutlets": amenities.get("Outlet Availability", 0) == 1,
        "preferQuiet": body.get("noise_level", -1) > 0 and body.get("noise_level", 5) <= 2,
        "maxDistanceMiles": maxDist,
        "preferLateHours": False,
    }


def createApp(dbPath: str = "data/studySpots.db") -> Flask:
    app = Flask(__name__)
    if CORS is not None:
        CORS(app)
    repo = SQLiteRepository(dbPath)
    repo.initialize()

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    @app.route("/save_preferences", methods=["POST"])
    def savePreferences():
        body = request.get_json(silent=True) or {}
        username = body.get("username", "").strip()
        if not username:
            return jsonify({"error": "username is required"}), 400
        translated = _translateFlutterPrefs(body)
        repo.saveUserPreferences(username, translated)
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
        savedPrefs = repo.getUserPreferences(username) if username else None
        prefData = savedPrefs if savedPrefs else body.get("preferences", {})
        prefs = UserPreferences.fromDict(prefData)
        context = RequestContext.fromDict(body.get("context", {}))
        bookmarkedKeys = repo.getBookmarkedKeys(username) if username else set()
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

    @app.route("/spots/<spotId>", methods=["GET"])
    def spotDetails(spotId: str):
        spot = repo.getSpotById(spotId)
        if spot is None:
            spot = repo.getSpotByKey(spotId)
        if spot is None:
            return jsonify({"error": "spot not found"}), 404
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

    @app.route("/bookmarks/add", methods=["POST"])
    def addBookmarkFlutter():
        body = request.get_json(silent=True) or {}
        username = body.get("username", "").strip()
        spotKey = body.get("spot_key", "").strip() or body.get("canonicalKey", "").strip()
        if not username or not spotKey:
            return jsonify({"error": "username and spot_key are required"}), 400
        repo.addBookmark(username, spotKey)
        return jsonify({"status": "bookmarked", "username": username, "spot_key": spotKey})

    @app.route("/bookmarks/remove", methods=["POST"])
    def removeBookmarkFlutter():
        body = request.get_json(silent=True) or {}
        username = body.get("username", "").strip()
        spotKey = body.get("spot_key", "").strip() or body.get("canonicalKey", "").strip()
        if not username or not spotKey:
            return jsonify({"error": "username and spot_key are required"}), 400
        repo.removeBookmark(username, spotKey)
        return jsonify({"status": "removed", "username": username, "spot_key": spotKey})

    return app