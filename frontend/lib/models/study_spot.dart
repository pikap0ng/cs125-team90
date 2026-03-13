class StudySpot {
  final String title;
  final String address;
  final String imagePath;
  final String status;
  final bool isOpen;
  final int travelTimeInMinutes;  // Minutes
  bool isBookmarked;

  final String operatingHours;
  final String phoneNumber;
  final double rating;
  final int reviewCount;
  final List<String> gallery;

  final String locationType;
  final bool hasOutlets;
  final bool isOnCampus;
  final bool hasOutdoorSeating;
  final bool isFreshmanOnly;
  final bool isBright;
  final String noiseLevel;
  final int distanceFromCampus;

  StudySpot({
    required this.title,
    required this.address,
    required this.status,
    required this.travelTimeInMinutes,
    required this.imagePath,
    required this.isOpen,
    required this.isBookmarked,

    this.operatingHours = "6:00am - 10:00pm",
    this.phoneNumber = "(000) 000 - 0000",
    this.rating = 0.0,
    this.reviewCount = 0,
    this.gallery = const [],
    this.locationType = "Unknown",
    this.hasOutlets = false,
    this.isOnCampus = false,
    this.hasOutdoorSeating = false,
    this.isFreshmanOnly = false,
    this.isBright = false,
    this.noiseLevel = "N/A",
    this.distanceFromCampus = 0,
  });

  String get travelTimeDisplay {
    if (travelTimeInMinutes >= 60) {
      int hours = travelTimeInMinutes ~/ 60;
      int mins = travelTimeInMinutes % 60;
      return mins > 0 ? "${hours}hr ${mins}min" : "${hours}hr";
    }
    return "$travelTimeInMinutes min";
  }
}