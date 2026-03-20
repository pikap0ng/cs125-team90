class StudySpot {
  final String title;
  final String address;
  final String imagePath;
  final String? networkImageUrl;
  final String status;
  final bool isOpen;
  final int travelTimeInMinutes;
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

  final String canonicalKey;
  final double score;
  final List<String> explanation;

  StudySpot({
    required this.title,
    required this.address,
    required this.status,
    required this.travelTimeInMinutes,
    required this.imagePath,
    required this.isOpen,
    required this.isBookmarked,
    this.networkImageUrl,

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
    this.canonicalKey = "",
    this.score = 0.0,
    this.explanation = const [],
  });

  factory StudySpot.fromBackend(Map<String, dynamic> json, {Set<String>? bookmarkedKeys}) {
    final features = json['features'] as Map<String, dynamic>? ?? {};
    final name = json['name'] as String? ?? 'Unknown';
    final onCampus = json['onCampus'] as bool? ?? false;
    final distMiles = (json['distanceMiles'] as num?)?.toDouble() ?? 0.0;
    final hoursText = features['hoursText'] as String? ?? '';
    final wifi = features['wifi'] as String? ?? '';
    final parking = features['parking'] as String? ?? '';
    final charging = features['charging'] as String? ?? '';
    final openNow = features['openNow'];
    final cKey = json['canonicalKey'] as String? ?? '';
    final photoUrl = features['photoUrl'] as String?;

    String locType = "Other";
    final lower = name.toLowerCase();
    if (lower.contains('library') || lower.contains('study') || lower.contains('learning')) {
      locType = "Library";
    } else if (lower.contains('cafe') || lower.contains('coffee') || lower.contains('tea')) {
      locType = "Cafe";
    }

    int travelMins = (distMiles / 3.0 * 60).round();
    if (travelMins < 1 && distMiles > 0) travelMins = 1;

    List<String> explanationList = [];
    if (json['explanation'] != null) {
      explanationList = List<String>.from(json['explanation']);
    }

    return StudySpot(
      title: name,
      address: json['address'] as String? ?? (onCampus ? 'UCI Campus' : 'Irvine, CA'),
      imagePath: _pickImage(name),
      networkImageUrl: (photoUrl != null && photoUrl.isNotEmpty) ? photoUrl : null,
      status: _scoreToStatus(json['score'] as num? ?? 0),
      isOpen: openNow == true,
      travelTimeInMinutes: travelMins,
      isBookmarked: bookmarkedKeys?.contains(cKey) ?? false,
      operatingHours: hoursText.isNotEmpty ? hoursText : "Hours not available",
      phoneNumber: "",
      rating: (json['score'] as num?)?.toDouble() ?? 0.0,
      locationType: locType,
      hasOutlets: charging.isNotEmpty || locType == "Library",
      isOnCampus: onCampus,
      hasOutdoorSeating: false,
      isFreshmanOnly: false,
      isBright: false,
      noiseLevel: locType == "Library" ? "Quiet" : "Moderate",
      distanceFromCampus: (distMiles * 1609).round(),
      canonicalKey: cKey,
      score: (json['score'] as num?)?.toDouble() ?? 0.0,
      explanation: explanationList,
    );
  }

  /// Returns true if this spot has a network photo from Google Places
  bool get hasNetworkImage => networkImageUrl != null && networkImageUrl!.isNotEmpty;

  String get travelTimeDisplay {
    if (travelTimeInMinutes >= 60) {
      int hours = travelTimeInMinutes ~/ 60;
      int mins = travelTimeInMinutes % 60;
      return mins > 0 ? "${hours}hr ${mins}min" : "${hours}hr";
    }
    return "$travelTimeInMinutes min";
  }

  static String _pickImage(String name) {
    final lower = name.toLowerCase();
    if (lower.contains('science library')) return 'assets/science_library.png';
    if (lower.contains('langson')) return 'assets/langson_library.png';
    if (lower.contains('student center')) return 'assets/student_center.png';
    return 'assets/langson_library.png';
  }

  static String _scoreToStatus(num score) {
    if (score >= 0.7) return "Great match";
    if (score >= 0.5) return "Good match";
    if (score >= 0.3) return "Fair match";
    return "Low match";
  }
}