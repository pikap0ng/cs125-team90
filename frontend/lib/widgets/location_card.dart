import 'package:flutter/material.dart';
import 'package:study_spot_locator/constants.dart';
import 'package:study_spot_locator/models/study_spot.dart';
import 'package:study_spot_locator/pages/details_page.dart';

class LocationCard extends StatefulWidget {
  final StudySpot spot;

  const LocationCard({
    super.key,
    required this.spot,
  });

  @override
  State<LocationCard> createState() => _LocationCardState();
}

class _LocationCardState extends State<LocationCard> {
  late bool _isBookmarked;
  @override
  void initState() {
    super.initState();
    _isBookmarked = widget.spot.isBookmarked;
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SelectableText(
          widget.spot.title,
          style: primaryTitleStyle.copyWith(fontSize: 18.0),
        ),
        const SizedBox(height: 8),
        InkWell(
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => DetailsPage(spot: widget.spot)),
            );
          },
          child: Container(
            decoration: BoxDecoration(
              color: primaryWhite,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: primaryBlack, width: 1.0),
            ),
            child: Column(
              children: [
                Stack(
                  children: [
                    ClipRRect(
                      borderRadius: const BorderRadius.vertical(top: Radius.circular(7)),
                      child: Image.asset(
                        widget.spot.imagePath,
                        height: 180,
                        width: double.infinity,  // Set to a max of __ and min of __
                        fit: BoxFit.cover,
                        errorBuilder: (context, error, stackTrace) {
                          return Container(
                            height: 180,
                            color: primaryGray,
                            alignment: Alignment.center,
                            child: const Icon(Icons.broken_image, color: primaryBlack, size: 40),
                          );
                        },
                      ),
                    ),
                    Positioned(
                      top: 10,
                      right: 10,
                      child: MouseRegion(
                        cursor: SystemMouseCursors.click,
                        child: GestureDetector(
                          onTap:() {
                            setState(() {
                              _isBookmarked = !_isBookmarked;
                            });
                          },
                          child: Container(
                            padding: const EdgeInsets.all(4),
                            decoration: BoxDecoration(
                              color: primaryLightGray,
                              shape: BoxShape.circle,
                            ),
                            child: Stack(
                              alignment: Alignment.center,
                              children: [
                                if (_isBookmarked)
                                  const Icon(
                                    Icons.bookmark, 
                                    color: primaryGold,
                                    size: 24,
                                  ),
                                const Icon(
                                  Icons.bookmark_outline_rounded,
                                  color: primaryBlack,
                                  size: 26,
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
                Container(
                  decoration: const BoxDecoration(
                    border: Border(
                      top: BorderSide(color: primaryBlack, width: 1),
                    ),
                  ),
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _infoRow(Icons.location_on_outlined, widget.spot.address),
                      const SizedBox(height: 8),
                      _infoRow(Icons.bar_chart, widget.spot.status),
                      const SizedBox(height: 8),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          _infoRow(Icons.timer_outlined, widget.spot.travelTimeDisplay),
                          Text(
                            widget.spot.isOpen ? "Open" : "Closed",
                            style: TextStyle(
                              color: widget.spot.isOpen ? primaryGreen : primaryRed,
                              fontWeight: FontWeight.bold,
                              fontFamily: 'Serif',
                            ),
                          ),
                        ],
                      )
                    ],
                  ),
                )
              ],
            ),
          ),
        )

      ],
    );
  }
  Widget _infoRow(IconData icon, String text) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 18, color: primaryBlack),
        const SizedBox(width: 8,),
        Flexible(
          child: Text(
            text,
            style: primaryTextStyle.copyWith(fontSize: 14),
          ),
        )
      ],
    );
  }
}

