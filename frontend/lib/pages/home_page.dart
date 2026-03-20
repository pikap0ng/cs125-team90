import 'package:flutter/material.dart';
import 'package:study_spot_locator/models/study_spot.dart';
import 'package:study_spot_locator/services/api_service.dart';
import 'package:study_spot_locator/widgets/location_card.dart';
import 'package:study_spot_locator/constants.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => HomePageState();
}

class HomePageState extends State<HomePage> {
  List<StudySpot> _bookmarkedSpots = [];
  bool _isLoading = true;
  String _errorMsg = "";

  @override
  void initState() {
    super.initState();
    _loadBookmarks();
  }

  Future<void> _loadBookmarks() async {
    setState(() {
      _isLoading = true;
      _errorMsg = "";
    });

    try {
      final spots = await ApiService.getBookmarkedSpots("username");
      if (!mounted) return;
      setState(() {
        _bookmarkedSpots = spots;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _errorMsg = "Could not load bookmarks.";
      });
    }
  }

  /// Called externally (e.g. from MainScreen) to refresh bookmarks
  void refresh() {
    _loadBookmarks();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SelectableText("Bookmarks", style: primaryTitleStyle),
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
                            onPressed: _loadBookmarks,
                            child: const Text("Retry"),
                          ),
                        ],
                      ),
                    ),
                  )
                else if (_bookmarkedSpots.isEmpty)
                  Center(
                    child: Padding(
                      padding: const EdgeInsets.only(top: 40),
                      child: Text(
                        "No bookmarks yet.\nTap the bookmark icon on any study spot to save it here.",
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
                      children: _bookmarkedSpots.map((spot) {
                        return ConstrainedBox(
                          constraints: const BoxConstraints(maxWidth: 400),
                          child: LocationCard(
                            spot: spot,
                            onBookmarkChanged: _loadBookmarks,
                          ),
                        );
                      }).toList(),
                    ),
                  ),
                const SizedBox(height: 25),
              ],
            ),
          ),
        ),
      ),
    );
  }
}