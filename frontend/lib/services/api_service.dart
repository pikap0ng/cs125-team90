import 'dart:convert';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;
import 'package:study_spot_locator/constants.dart';
import 'package:study_spot_locator/models/study_spot.dart';

class ApiService {
  static String get baseUrl => dotenv.get('API_BASE_URL', fallback: 'http://localhost:5000');

  /// Fetch ranked study spot recommendations from the backend.
  ///
  /// [username] is used to load saved preferences and bookmarks server-side.
  /// [query] is an optional free-text search filter.
  /// [onCampusOnly] restricts results to on-campus spots when true.
  static Future<List<StudySpot>> getRecommendations({
    required String username,
    String? query,
    bool onCampusOnly = false,
    int topK = 20,
  }) async {
    final url = Uri.parse('$baseUrl/recommendations');

    try {
      // Build context object for the request
      final Map<String, dynamic> context = {};
      if (query != null && query.trim().isNotEmpty) {
        context['query'] = query.trim();
      }
      if (onCampusOnly) {
        context['onCampusOnly'] = true;
      }

      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "username": username,
          "context": context,
          "topK": topK,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final results = data['results'] as List<dynamic>? ?? [];

        // Fetch bookmarks so we can mark spots as bookmarked
        final bookmarks = await getUserBookmarks(username);
        final bookmarkSet = bookmarks.toSet();

        return results
            .map((json) => StudySpot.fromBackend(
                  json as Map<String, dynamic>,
                  bookmarkedKeys: bookmarkSet,
                ))
            .toList();
      } else {
        print("Recommendations error: ${response.statusCode} ${response.body}");
        return [];
      }
    } catch (e) {
      print("Connection Error (recommendations): $e");
      return [];
    }
  }

  static Future<bool> saveUserPreferences({
    required String username,
    required double noise,
    required double distance,
    required Map<String, Preference> amenities,
    required Map<String, Preference> locationType,
  }) async {
    final url = Uri.parse('$baseUrl/save_preferences');

    try {
      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "username": username,
          "noise_level": noise,
          "max_distance": distance,
          "amenities": amenities.map((key, value) => MapEntry(key, prefToInt(value))),
          "location_type": locationType.map((key, value) => MapEntry(key, prefToInt(value))),
        })
      );
      return response.statusCode == 200;
    } catch (e) {
      print("Connection Error: $e");
      return false;
    }
  }

  static Future<List<String>> getUserBookmarks(String username) async {
    final url = Uri.parse('$baseUrl/bookmarks/$username');
    
    try {
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return List<String>.from(data['bookmarks']);
      } else {
        return [];
      }
    } catch (e) {
      print("Error fetching bookmarks: $e");
      return [];
    }
  }

  static Future<bool> toggleBookmark(String username, String spotKey, bool isAdding) async {
    final endpoint = isAdding ? '/bookmarks/add' : '/bookmarks/remove';
    final url = Uri.parse('$baseUrl$endpoint');

    try {
      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "username": username,
          "spot_key": spotKey,
        }),
      );
      return response.statusCode == 200;
    } catch (e) {
      print("Bookmark Toggle Error: $e");
      return false;
    }
  }

}