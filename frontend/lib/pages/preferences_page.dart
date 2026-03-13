import 'package:flutter/material.dart';
import 'package:study_spot_locator/constants.dart';

class PreferencesPage extends StatefulWidget {
  const PreferencesPage({super.key});

  @override
  State<PreferencesPage> createState() => _PreferencesPageState();
}

class _PreferencesPageState extends State<PreferencesPage> {
  double _noiseLevel = 3;
  double _distance = 10;
  bool _libraryChecked = true;
  bool _cafeChecked = true;
  bool _otherChecked = false;

  final Map<String, bool> _preferences = {
    "On Campus": true,
    "Outlet Availability": true,
    "Outdoor Seating Availability": false,
    "Bright": false,
    "Freshman-Only": false,
  };


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                ElevatedButton(
                  onPressed: () => Navigator.pushReplacementNamed(context, '/loginpage'),
                  style: ElevatedButton.styleFrom(
                    elevation: 0,
                  ),
                  child: const Text("Logout"),
                ),
              ],
            ),
            const SelectableText("Preferences", style: primaryTitleStyle),
            const Divider(color: primaryBlack, thickness: 1.5),
            const SelectableText("Your choices will affect suggestions and search results.", style: TextStyle(fontSize: 12, fontStyle: FontStyle.italic),),
            const SizedBox(height: 20,),

            _buildContainerSection([
              _buildCheckOption("On Campus"),
              _buildCheckOption("Outlet Availability"),
              _buildCheckOption("Outdoor Seating Availablily"),
              _buildCheckOption("Bright"),
              _buildCheckOption("Freshman-Only"),
            ]),
            
            const SizedBox(height: 20,),

            _buildContainerSection([
              const Text("Noise Tolerance", style: primaryTextStyle),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text("1", style: const TextStyle(fontSize: 14),),
                  Expanded(
                    child: Slider(
                      value: _noiseLevel,
                      min: 1, max: 5, divisions: 4,
                      activeColor: darkPrimaryColor,
                      onChanged: (value) => setState(() {
                        _noiseLevel = value;
                      }),
                    ),
                  ),
                  Text("5", style: const TextStyle(fontSize: 14),),
                ],
              ),
              const SizedBox(height: 10),

              const Text("Maximum Distance From Campus", style: primaryTextStyle),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text("0", style: const TextStyle(fontSize: 14),),
                  Expanded(
                    child: Slider(
                      value: _distance,
                      min: 0, max: 25,
                      activeColor: darkPrimaryColor,
                      onChanged: (value) => setState(() {
                        _distance = value;
                      }),
                    ),
                  ),
                  Text("25", style: const TextStyle(fontSize: 14),),
                ],
              ),
              const SizedBox(height: 10),
            ]),
            const SizedBox(height: 20),
            _buildContainerSection([
              const Text("Location Type"),
              Row(
                children: [
                  _buildSmallCheckbox("Library", _libraryChecked, (v) => setState(() => _libraryChecked = v!)),
                  _buildSmallCheckbox("Cafe", _cafeChecked, (v) => setState(() => _cafeChecked = v!)),
                  _buildSmallCheckbox("Other", _otherChecked, (v) => setState(() => _otherChecked = v!)),
                ],
              ),
            ]),
          ],
        ),
      ),
    );
  }

  Widget _buildContainerSection(List<Widget> children) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: lightPrimaryColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: primaryBlack),
        boxShadow: [
          BoxShadow(color: primaryBlack.withAlpha(25), blurRadius: 4, offset: const Offset(0, 2)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: children,
      ),
    );
  }

  Widget _buildCheckOption(String title) {
    bool isChecked = _preferences[title] ?? false;
    return InkWell(
      onTap: () {
        setState(() {
          _preferences[title] = !isChecked;
        });
      },
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
        child: Row(
          children: [
            Icon(
              isChecked ? Icons.check_circle_rounded : Icons.circle_outlined,
              color: darkPrimaryColor,
            ),
            const SizedBox(width: 12,),
            Text(title, style: primaryTextStyle),
          ],
        ),
      ),
    );
  }

  Widget _buildSmallCheckbox(String title, bool value, Function(bool?) onChanged) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Checkbox(value: value, onChanged: onChanged,  activeColor: darkPrimaryColor,),
        Text(title, style: const TextStyle(fontSize: 12)),
        const SizedBox(width: 10,),
      ],
    );
  }

}