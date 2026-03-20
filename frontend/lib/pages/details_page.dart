import 'package:flutter/material.dart';
import 'package:study_spot_locator/constants.dart';
import 'package:study_spot_locator/models/study_spot.dart';
import 'package:study_spot_locator/services/api_service.dart';

class DetailsPage extends StatefulWidget{
  final StudySpot spot;
  const DetailsPage({super.key, required this.spot});

  @override
  State<DetailsPage> createState() => _DetailsPageState();
}

class _DetailsPageState extends State<DetailsPage> {
  late bool _isBookmarked;

  @override
  void initState() {
    super.initState();
    _isBookmarked = widget.spot.isBookmarked;
  }

  void _toggleBookmark() async {
    final newState = !_isBookmarked;
    setState(() {
      _isBookmarked = newState;
      widget.spot.isBookmarked = newState;
    });

    final success = await ApiService.toggleBookmark(
      "username",
      widget.spot.canonicalKey,
      newState,
    );

    if (!success && mounted) {
      setState(() {
        _isBookmarked = !newState;
        widget.spot.isBookmarked = !newState;
      });
    }
  }

  Widget _buildSpotImage({required double height, BoxFit fit = BoxFit.contain}) {
    if (widget.spot.hasNetworkImage) {
      return Image.network(
        widget.spot.networkImageUrl!,
        height: height,
        width: double.infinity,
        fit: fit,
        loadingBuilder: (context, child, loadingProgress) {
          if (loadingProgress == null) return child;
          return Container(
            height: height,
            color: lightPrimaryColor,
            alignment: Alignment.center,
            child: const CircularProgressIndicator(
              color: darkPrimaryColor,
              strokeWidth: 2,
            ),
          );
        },
        errorBuilder: (context, error, stackTrace) {
          return Image.asset(
            widget.spot.imagePath,
            height: height,
            width: double.infinity,
            fit: fit,
          );
        },
      );
    }

    return Image.asset(
      widget.spot.imagePath,
      height: height,
      width: double.infinity,
      fit: fit,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Transform.translate(
                    offset: const Offset(-12, 0),
                    child: IconButton(
                      constraints: const BoxConstraints(),
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18, color: primaryBlack),
                    ),
                  ),
                  MouseRegion(
                    cursor: SystemMouseCursors.click,
                    child: GestureDetector(
                      onTap: _toggleBookmark,
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          if (_isBookmarked)
                            const Icon(
                              Icons.bookmark,
                              color: primaryGold,
                              size: 26,
                            ),
                          const Icon(
                            Icons.bookmark_outline_rounded,
                            color: primaryBlack,
                            size: 30,
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              Text(widget.spot.title, style: primaryTitleStyle.copyWith(fontSize: 32)),
              const Divider(color: primaryBlack, thickness: 1.5),
              const SizedBox(height: 20),

              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: _buildSpotImage(height: 200, fit: BoxFit.cover),
              ),
              if (!widget.spot.hasNetworkImage)
                const Center(
                  child: Padding(
                    padding: EdgeInsets.all(8.0),
                    child: Text("● ○ ○ ○ ○ ○", style: TextStyle(color: primaryGray))
                  ),
                )
              else
                const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  border: Border.all(color: primaryBlack),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Column(
                  children: [
                    _infoRow(Icons.location_on_outlined, widget.spot.address),
                    _infoRow(Icons.star, "${widget.spot.rating} (${widget.spot.reviewCount})", isRating: true),
                    _infoRow(Icons.access_time, widget.spot.operatingHours),
                    _infoRow(Icons.bar_chart_rounded, widget.spot.status),
                    _infoRow(Icons.phone, widget.spot.phoneNumber),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              const Text("Additional Details", style: primaryTextStyle),
              const SizedBox(height: 10),
              _buildDetailsBox(widget.spot),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailsBox(StudySpot spot) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: lightPrimaryColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: primaryBlack),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _detailText("Location Type: ${widget.spot.locationType}"),
          _detailText("Place: ${widget.spot.isOnCampus ? "On Campus" : "Off Campus"}"),
          _detailText("Outlets: ${widget.spot.hasOutlets ? "Yes" : "No"}"),
          _detailText("Outdoor Seating: ${widget.spot.hasOutdoorSeating ? "Yes": "No"}"),
          _detailText("Freshman-Only: ${widget.spot.isFreshmanOnly ? "Yes" : "No"}"),
          _detailText("Bright: ${widget.spot.isBright ? "Yes": "No"}"),
          _detailText("Noise Level: ${widget.spot.noiseLevel}"),
          _detailText("Distance from campus: ${widget.spot.distanceFromCampus}m"),
          _detailText("ETA: ${widget.spot.travelTimeDisplay}"),
        ],
      ),
    );
  }

  Widget _detailText(String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Text(text, style: const TextStyle(fontSize: 15, color: primaryBlack)),
    );
  }

  Widget _infoRow(IconData icon, String text, {bool isRating = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(icon, size: 20, color: isRating ? primaryGold : primaryBlack),
          const SizedBox(width: 10),
          Expanded(child: SelectableText(text)),
        ],
      ),
    );
  }
}