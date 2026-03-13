import 'package:flutter/material.dart';
import 'package:study_spot_locator/pages/home_page.dart';
import 'package:study_spot_locator/pages/preferences_page.dart';
import 'package:study_spot_locator/pages/search_page.dart';
import 'package:study_spot_locator/constants.dart';

class MainScreen extends StatefulWidget{
  const MainScreen({super.key});
  
  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedIndex = 0;
  
  final List<Widget> _pages = [
    const HomePage(),
    const SearchPage(),
    const PreferencesPage(),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _selectedIndex,
        children: _pages,
      ),
      bottomNavigationBar: Container(
        height: 65,
        decoration: const BoxDecoration(
          color: darkPrimaryColor,
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            Expanded(child: _buildNavIcon(Icons.home_filled, 0)),
            Expanded(child: _buildNavIcon(Icons.search, 1)),
            Expanded(child: _buildNavIcon(Icons.person, 2)),
          ],
        ),
      ),

    );
  }

  Widget _buildNavIcon(IconData icon, int index) {
  bool isSelected = _selectedIndex == index;
  return GestureDetector(
    onTap:() => _onItemTapped(index),
    behavior: HitTestBehavior.opaque,
    child: Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(icon, size: 30, color: isSelected ? primaryBlack : primaryLightGray,),
        if (isSelected)
          Container(
            margin: const EdgeInsets.only(top: 4),
            height: 2,
            width: 25,
            color: primaryBlack,
          )
        else
          const SizedBox(height: 6),
      ],
    ),
  );
}

}