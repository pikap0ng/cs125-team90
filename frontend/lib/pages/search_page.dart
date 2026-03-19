import 'package:flutter/material.dart';
import 'package:study_spot_locator/models/study_spot.dart';
import 'package:study_spot_locator/widgets/location_card.dart';
import 'package:study_spot_locator/constants.dart';

class SearchPage extends StatefulWidget {
  const SearchPage({super.key});

  @override
  State<SearchPage> createState() => _SearchPageState();
}

class _SearchPageState extends State<SearchPage> {
  final List<StudySpot> spots = [
    // Make dynamically later
    StudySpot(
      title: "Science Library",
      address: "510 E Peltason Dr, Irvine, CA 92617",
      status: "Very busy",
      travelTimeInMinutes: 10,
      imagePath: "assets/science_library.png",
      isOpen: false,
      isBookmarked: true,
    ),
    StudySpot(
      title: "UCI Student Center",
      address: "510 E Peltason Dr, Irvine, CA 92617",
      status: "Moderate",
      travelTimeInMinutes: 15,
      imagePath: "assets/student_center.png",
      isOpen: true,
      isBookmarked: false,
    ),
  ];

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
              decoration: InputDecoration(
                hintText: "Search",
                prefixIcon: const Icon(Icons.search, size: 30, color: primaryBlack),
              ),
            ),
            const SizedBox(height: 15,),


            // const Text("Recent Searches", style: TextStyle(fontWeight: FontWeight.bold)),
            // const SizedBox(height: 8),
            // _buildRecentSearchItem(""),
            // const SizedBox(height: 5),
            // _buildRecentSearchItem(""),
            // const SizedBox(height: 25),


            const Text("Suggested", style: primaryTitleStyle,),
            const Divider(color: primaryBlack, thickness: 1.5,),
            const SizedBox(height: 15,),

            Center(
              child: Wrap(
                spacing: 20,
                runSpacing: 20,
                alignment: WrapAlignment.center,
                children: spots.map((spot) {
                  return ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 400),
                    child: LocationCard(spot: spot),
                  );
                }).toList(),
              ),
            )
          ],
        ),
      )
    );
  }

  // Widget _buildRecentSearchItem(String text) {
  //   return Container(
  //     height: 35,
  //     width: double.infinity,
  //     padding: const EdgeInsets.symmetric(horizontal: 15),
  //     decoration: BoxDecoration(
  //       color: primaryGray,
  //       borderRadius: BorderRadius.circular(4),
  //     ),
  //     child: const Align(
  //       alignment: Alignment.centerRight,
  //       child: Icon(Icons.north_west, size: 16, color: primaryBlack),
  //     ),
  //   );
  // }

}