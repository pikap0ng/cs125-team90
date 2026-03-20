import 'package:flutter/material.dart';
import 'package:study_spot_locator/constants.dart';
import 'package:study_spot_locator/models/study_spot.dart';
import 'package:study_spot_locator/pages/details_page.dart';
import 'package:study_spot_locator/services/api_service.dart';

class LocationCard extends StatefulWidget {
  final StudySpot spot;
  final VoidCallback? onBookmarkChanged;

  const LocationCard({
    super.key,
    required this.spot,
    this.onBookmarkChanged,
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
  void didUpdateWidget(covariant LocationCard oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.spot.isBookmarked != widget.spot.isBookmarked) {
      _isBookmarked = widget.spot.isBookmarked;
    }
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
    } else if (success) {
      widget.onBookmarkChanged?.call();
    }
  }

  Widget _buildSpotImage({required double height, BoxFit fit = BoxFit.cover}) {
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
          // Fall back to asset image on network error
          return Image.asset(
            widget.spot.imagePath,
            height: height,
            width: double.infinity,
            fit: fit,
            errorBuilder: (context, error, stackTrace) {
              return Container(
                height: height,
                color: primaryGray,
                alignment: Alignment.center,
                child: const Icon(Icons.broken_image, color: primaryBlack, size: 40),
              );
            },
          );
        },
      );
    }

    return Image.asset(
      widget.spot.imagePath,
      height: height,
      width: double.infinity,
      fit: fit,
      errorBuilder: (context, error, stackTrace) {
        return Container(
          height: height,
          color: primaryGray,
          alignment: Alignment.center,
          child: const Icon(Icons.broken_image, color: primaryBlack, size: 40),
        );
      },
    );
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
          onTap: () async {
            await Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => DetailsPage(spot: widget.spot)),
            );
            if (mounted) {
              setState(() {
                _isBookmarked = widget.spot.isBookmarked;
              });
              widget.onBookmarkChanged?.call();
            }
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
                      child: _buildSpotImage(height: 180),
                    ),
                    Positioned(
                      top: 10,
                      right: 10,
                      child: MouseRegion(
                        cursor: SystemMouseCursors.click,
                        child: GestureDetector(
                          onTap: _toggleBookmark,
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
                      if (widget.spot.explanation.isNotEmpty)
                        Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: Wrap(
                            spacing: 6,
                            runSpacing: 4,
                            children: widget.spot.explanation
                                .where((e) => e.contains("(+)"))
                                .take(3)
                                .map((e) => Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                      decoration: BoxDecoration(
                                        color: darkPrimaryColor.withAlpha(25),
                                        borderRadius: BorderRadius.circular(12),
                                      ),
                                      child: Text(
                                        e.replaceAll("(+)", "").trim(),
                                        style: const TextStyle(fontSize: 11, color: darkPrimaryColor),
                                      ),
                                    ))
                                .toList(),
                          ),
                        ),
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
        const SizedBox(width: 8),
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