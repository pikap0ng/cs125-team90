import 'package:flutter/material.dart';

// --- Colors ---
const Color darkPrimaryColor = Color(0xFF6D8196);
const Color lightPrimaryColor = Color(0xFFEAECF2);
const Color primaryBlack = Color(0xFF232323);
const Color primaryGray = Color(0xFFCBCBCB);
const Color primaryWhite = Color(0xFFF4F4F4);
const Color primaryGold = Color(0xFFFFD16F);
const Color primaryGreen = Color(0xFF197F29);
const Color primaryLightGray = Color(0xFFD9D9D9);
const Color primaryRed = Color(0xFFD71F1F);


// --- Text Styles ---
const TextStyle primaryTitleStyle = TextStyle(
  fontSize: 30,
  fontWeight: FontWeight.bold,
  fontFamily: 'Serif',
  color: primaryBlack,
  height: 1.2,
);

const TextStyle primaryTextStyle = TextStyle(
  fontSize: 16,
  color: primaryBlack,
);

const TextStyle secondaryTextStyle = TextStyle(
  fontSize: 16,
  color: primaryWhite,
);

const TextStyle primaryErrorStyle = TextStyle(
  fontSize: 14,
  color: primaryRed,
  fontWeight: FontWeight.w500,
);


enum Preference { none, prefer, avoid }

int prefToInt(Preference p) {
  switch (p) {
    case Preference.prefer: return 1;
    case Preference.avoid: return -1;
    case Preference.none: return 0;
  }
}