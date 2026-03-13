import 'package:flutter/material.dart';
import 'package:study_spot_locator/models/study_spot.dart';
import 'package:study_spot_locator/widgets/location_card.dart';
import 'package:study_spot_locator/constants.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {

  final List<StudySpot> spots = [
    // Make dynamically later using query/stored
    StudySpot(
      title: "Science Library",
      address: "510 E Peltason Dr, Irvine, CA 92617",
      status: "Very busy",
      travelTimeInMinutes: 10,
      imagePath: "assets/science_library.png",
      isOpen: true,
      isBookmarked: true,
    ),
    StudySpot(
      title: "Langson Library",
      address: "UCI Campus",
      status: "Moderate",
      travelTimeInMinutes: 5,
      imagePath: "assets/langson_library.png",
      isOpen: true,
      isBookmarked: false,
    ),
    StudySpot(
      title: "Langson Library",
      address: "UCI Campus",
      status: "Moderate",
      travelTimeInMinutes: 5,
      imagePath: "assets/langson_library.png",
      isOpen: true,
      isBookmarked: false,
    ),
    StudySpot(
      title: "Langson Library",
      address: "UCI Campus",
      status: "Moderate",
      travelTimeInMinutes: 5,
      imagePath: "assets/langson_library.png",
      isOpen: true,
      isBookmarked: false,
    ),
  ];


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SelectableText("Bookmarks", style: primaryTitleStyle),
                  const Divider(color: primaryBlack, thickness: 1.5),
                  const SizedBox(height: 15,),

                  // SizedBox(
                  //   width: double.infinity,
                  //   height: 45,
                  //   child: ElevatedButton(
                  //     onPressed: () {},
                  //     style: ElevatedButton.styleFrom(
                  //       backgroundColor: primaryGray,
                  //       foregroundColor: primaryBlack,
                  //       elevation: 0,
                  //       shape: const RoundedRectangleBorder(
                  //         borderRadius: BorderRadius.zero,
                  //       ),
                  //     ),
                  //     child: const Text(
                  //       "Sort Placeholder",
                  //       style: primaryTextStyle,
                  //     ),
                  //   ),
                  // ),
                ],
              ),
            ),
            const SizedBox(height: 10,),

            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.all(20),
                itemCount: spots.length,
                itemBuilder:(context, index) {
                  final spot = spots[index];
                  
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 25),
                    child: LocationCard(spot: spot,),
                  );
                },
              ),
            )
          ],
        ),
      ),
    );
  }

}