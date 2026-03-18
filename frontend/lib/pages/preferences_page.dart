import 'package:flutter/material.dart';
import 'package:study_spot_locator/constants.dart';
import 'package:study_spot_locator/services/api_service.dart';

class PreferencesPage extends StatefulWidget {
  const PreferencesPage({super.key});

  @override
  State<PreferencesPage> createState() => _PreferencesPageState();
}

class _PreferencesPageState extends State<PreferencesPage> {
  bool _isLoading = false;

  double _noiseLevel = 1;
  double _distance = 0;
  bool _useNoisePref = false;
  bool _useDistancePref = false;

  final Map<String, Preference> _locationTypePrefs = {
    "Library": Preference.none,
    "Cafe": Preference.none,
    "Other": Preference.none,
  };

  final Map<String, Preference> _preferences = {
    "On Campus": Preference.none,
    "Outlet Availability": Preference.none,
    "Outdoor Seating Availability": Preference.none,
    "Bright": Preference.none,
    "Freshman-Only": Preference.none,
  };

  void _handleSave() async {
    setState(() {
      _isLoading = true;
    });

    bool success = await ApiService.saveUserPreferences(
      username: "username",
      noise: _useNoisePref ? _noiseLevel : -1.0,
      distance: _useDistancePref ? _distance : -1.0,
      amenities: _preferences,
      locationType: _locationTypePrefs
    );

    if (!mounted) return;

    setState(() {
      _isLoading = false;
    });

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Preferences Saved!")),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Failed to save."), backgroundColor: primaryRed,),
      );
    }
  }

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
              ..._preferences.keys.map((key) => _buildCheckOption(key)).toList(),
            ]),
            
            const SizedBox(height: 20,),

            _buildContainerSection([
              _buildSliderWithToggle(label: "Noise Tolerance", value: _noiseLevel, isEnabled: _useNoisePref, min: 1, max: 5, divisions: 4, onToggle: (v) => setState(() => _useNoisePref = v!), onChanged: (v) => setState(() => _noiseLevel = v)),
              const SizedBox(height: 5,),
              _buildSliderWithToggle(label: "Distance From Campus", value: _distance, isEnabled: _useDistancePref, min: 0, max: 25, divisions: 25, onToggle: (v) => setState(() => _useDistancePref = v!), onChanged: (v) => setState(() => _distance = v)),
            ]),
            
            const SizedBox(height: 20),
            _buildContainerSection([
              const Text("Location Type"),
              Row(
                children: [
                  Wrap(
                    children: _locationTypePrefs.keys.map((type) {
                      return _buildSmallCheckbox(type, _locationTypePrefs[type]!, (v) => setState(() => _locationTypePrefs[type] = v));
                    }).toList(),
                  )
                ],
              ),
            ]),
            const SizedBox(height: 15,),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    disabledBackgroundColor: darkPrimaryColor,
                  ),
                  onPressed: _isLoading ? null : _handleSave, 
                  child: _isLoading ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(color: primaryWhite, backgroundColor: Colors.transparent, strokeWidth: 2,),) : const Text("Save Changes"),
                ),
              ],
            ),
            const SizedBox(height: 35,),
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
    Preference current = _preferences[title] ?? Preference.none;
    IconData icon;

    switch (current) {
      case Preference.prefer:
        icon = Icons.check_circle;
        break;
      case Preference.avoid:
        icon = Icons.cancel_rounded;
        break;
      case Preference.none:
        icon = Icons.circle_outlined;
        break;
    }

    return InkWell(
      onTap: () {
        setState(() {
          if (current == Preference.none) {
            _preferences[title] = Preference.prefer;
          } else if (current == Preference.prefer) {
            _preferences[title] = Preference.avoid;
          } else {
            _preferences[title] = Preference.none;
          }
        });
      },
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 10,),
        child: Row(
          children: [
            Icon(icon, color: darkPrimaryColor, size: 28),
            const SizedBox(width: 15,),
            Text(title, style: primaryTextStyle),
            const Spacer(),
            Text(current.name.toUpperCase(), style: TextStyle(fontSize: 10, color: darkPrimaryColor.withAlpha(178))),
          ],
        ),
      ),
    );
  }

  Widget _buildSliderWithToggle({
    required String label,
    required double value,
    required bool isEnabled,
    required double min,
    required double max,
    int? divisions,
    required ValueChanged<bool?> onToggle,
    required ValueChanged<double> onChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: primaryTextStyle,),
            Row(
              children: [
                const Text("N/A", style: TextStyle(fontSize: 12),),
                Checkbox(value: !isEnabled, onChanged: (v) => onToggle(!v!)),
              ],
            ),
          ],
        ),
        Row(
          children: [
            Text(min.round().toString()),
            Expanded(
              child: Slider(
                value: value,
                min: min, max: max,
                divisions: divisions,
                label: value.round().toString(),
                activeColor: isEnabled ? darkPrimaryColor : primaryLightGray,
                onChanged: isEnabled ? onChanged : null,
              ),
            ),
            Text(max.round().toString()),
          ],
        ),
      ],
    );
  }

  Widget _buildSmallCheckbox(String title, Preference value, Function(Preference) onChanged) {
    IconData icon;

    switch(value) {
      case Preference.prefer:
        icon = Icons.check_box;
        break;
      case Preference.avoid:
        icon = Icons.disabled_by_default_rounded;
        break;
      case Preference.none:
        icon = Icons.check_box_outline_blank_rounded;
    }
    return InkWell(
      onTap: () {
        if (value == Preference.none) {
          onChanged(Preference.prefer);
        } else if (value == Preference.prefer) {
          onChanged(Preference.avoid);
        } else {
          onChanged(Preference.none);
        }
      },
      child: Padding(
        padding: const EdgeInsets.only(right: 12.0, top: 8, bottom: 8),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: darkPrimaryColor, size: 24),
            const SizedBox(width: 4,),
            Text(title, style: const TextStyle(fontSize: 13)),
          ],
        ),
      ),
    );
  }
}