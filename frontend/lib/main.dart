import 'package:flutter/material.dart';
import 'package:study_spot_locator/main_screen.dart';
import 'package:study_spot_locator/pages/home_page.dart';
import 'package:study_spot_locator/pages/login_page.dart';
import 'package:study_spot_locator/pages/preferences_page.dart';
import 'package:study_spot_locator/pages/search_page.dart';
import 'package:study_spot_locator/constants.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Study Spot Locator',
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: primaryWhite,
        colorScheme: ColorScheme.fromSeed(
          seedColor: darkPrimaryColor,
          primary: darkPrimaryColor,
          surface: primaryWhite,
        ),
        textSelectionTheme: const TextSelectionThemeData(
          cursorColor: primaryBlack,
          selectionHandleColor: primaryBlack,
          selectionColor: primaryGray,
        ),
        textTheme: TextTheme(
          bodyLarge: primaryTextStyle,
          bodyMedium: primaryTextStyle,
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: lightPrimaryColor,
          isDense: true, 
          contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
          hintStyle: primaryTextStyle.copyWith(color: Colors.black54),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(30),
            borderSide: const BorderSide(color: primaryBlack, width: 1.5),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(30),
            borderSide: const BorderSide(color: primaryBlack, width: 1.5),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(30),
            borderSide: const BorderSide(color: primaryBlack, width: 1.5),
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: darkPrimaryColor,
            foregroundColor: primaryWhite,
            elevation: 0,
            textStyle: secondaryTextStyle,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: const BorderSide(color: primaryBlack, width: 1.5),
            )
          )
        )
      ),
      home: const LoginPage(),
      routes: {
        '/mainscreen': (context) => const MainScreen(),
        '/homepage': (context) => const HomePage(),
        '/loginpage': (context) => const LoginPage(),
        '/searchpage': (context) => const SearchPage(),
        '/preferencespage': (context) => const PreferencesPage(),
      },
    );
  }
}

