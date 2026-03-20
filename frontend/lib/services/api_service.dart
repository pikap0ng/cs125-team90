import 'dart:convert';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;
import 'package:study_spot_locator/constants.dart';

class ApiService {
  static String get baseUrl => dotenv.get('API_BASE_URL', fallback: 'http://localhost:5000');


  static Future<Map<String, dynamic>?> login(String username, String password) async {
    final url = Uri.parse('$baseUrl/login');
    try {
      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "username": username,
          "password": password,
        }),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
    } catch (e) {
      print("Login Error: $e");
    }
    return null;
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
        }),
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
      }
    } catch (e) {
      print("Error fetching bookmarks: $e");
    }
    return [];
  }

  static Future<bool> toggleBookmark(String username, String spotKey, bool isAdding) async {
    final url = Uri.parse('$baseUrl/bookmarks');
    
    try {
      final response = isAdding 
        ? await http.post(
            url,
            headers: {"Content-Type": "application/json"},
            body: jsonEncode({"username": username, "canonicalKey": spotKey}),
          )
        : await http.delete(
            url,
            headers: {"Content-Type": "application/json"},
            body: jsonEncode({"username": username, "canonicalKey": spotKey}),
          );

      return response.statusCode == 200;
    } catch (e) {
      print("Bookmark Toggle Error: $e");
      return false;
    }
  }

  static Future<List<dynamic>> getRecommendations({
    required String username,
    required double userLat,
    required double userLon,
    int topK = 10,
  }) async {
    final url = Uri.parse('$baseUrl/recommendations');

    try {
      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "username": username,
          "topK": topK,
          "context": {
            "latitude": userLat,
            "longitude": userLon,
            "currentTime": DateTime.now().toIso8601String(),
          }
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['results'];
      }
    } catch (e) {
      print("Recommendations Error: $e");
    }
    return [];
  }

}