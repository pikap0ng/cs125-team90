import 'dart:async';
import 'package:flutter/material.dart';
import 'package:study_spot_locator/models/study_spot.dart';
import 'package:study_spot_locator/services/api_service.dart';
import 'package:study_spot_locator/widgets/location_card.dart';
import 'package:study_spot_locator/constants.dart';

class SearchPage extends StatefulWidget {
  const SearchPage({super.key});

  @override
  State<SearchPage> createState() => SearchPageState();
}

class SearchPageState extends State<SearchPage> {
  final TextEditingController _searchController = TextEditingController();
  Timer? _debounce;

  List<StudySpot> _spots = [];
  bool _isLoading = true;
  String _errorMsg = "";

  @override
  void initState() {
    super.initState();
    _loadRecommendations();
  }

  @override
  void dispose() {
    _searchController.dispose();
    _debounce?.cancel();
    super.dispose();
  }

  /// Called externally (e.g. from MainScreen) to re-fetch results.
  /// This picks up preference changes saved on the Preferences tab.
  void refresh() {
    _loadRecommendations(
      query: _searchController.text.isEmpty ? null : _searchController.text,
    );
  }

  Future<void> _loadRecommendations({String? query}) async {
    setState(() {
      _isLoading = true;
      _errorMsg = "";
    });

    try {
      final results = await ApiService.getRecommendations(
        username: "username",
        query: query,
        topK: 20,
      );

      if (!mounted) return;

      setState(() {
        _spots = results;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _errorMsg = "Could not connect to server.";
      });
    }
  }

  void _onSearchChanged(String text) {
    _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 400), () {
      _loadRecommendations(query: text.isEmpty ? null : text);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 40),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            TextField(
              controller: _searchController,
              onChanged: _onSearchChanged,
              decoration: InputDecoration(
                hintText: "Search",
                prefixIcon: const Icon(Icons.search, size: 30, color: primaryBlack),
              ),
            ),
            const SizedBox(height: 15),

            Text(
              _searchController.text.isEmpty ? "Suggested" : "Results",
              style: primaryTitleStyle,
            ),
            const Divider(color: primaryBlack, thickness: 1.5),
            const SizedBox(height: 15),

            if (_isLoading)
              const Center(
                child: Padding(
                  padding: EdgeInsets.only(top: 40),
                  child: CircularProgressIndicator(color: darkPrimaryColor),
                ),
              )
            else if (_errorMsg.isNotEmpty)
              Center(
                child: Padding(
                  padding: const EdgeInsets.only(top: 40),
                  child: Column(
                    children: [
                      const Icon(Icons.wifi_off_rounded, size: 40, color: primaryGray),
                      const SizedBox(height: 12),
                      Text(_errorMsg, style: primaryTextStyle.copyWith(color: primaryGray)),
                      const SizedBox(height: 12),
                      ElevatedButton(
                        onPressed: () => _loadRecommendations(
                          query: _searchController.text.isEmpty ? null : _searchController.text,
                        ),
                        child: const Text("Retry"),
                      ),
                    ],
                  ),
                ),
              )
            else if (_spots.isEmpty)
              Center(
                child: Padding(
                  padding: const EdgeInsets.only(top: 40),
                  child: Text(
                    _searchController.text.isEmpty
                        ? "No study spots found.\nRun the ingestion pipeline first."
                        : "No results for \"${_searchController.text}\"",
                    style: primaryTextStyle.copyWith(color: primaryGray),
                    textAlign: TextAlign.center,
                  ),
                ),
              )
            else
              Center(
                child: Wrap(
                  spacing: 20,
                  runSpacing: 20,
                  alignment: WrapAlignment.center,
                  children: _spots.map((spot) {
                    return ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 400),
                      child: LocationCard(
                        spot: spot,
                        onBookmarkChanged: () {
                          _loadRecommendations(
                            query: _searchController.text.isEmpty ? null : _searchController.text,
                          );
                        },
                      ),
                    );
                  }).toList(),
                ),
              ),
          ],
        ),
      ),
    );
  }
}