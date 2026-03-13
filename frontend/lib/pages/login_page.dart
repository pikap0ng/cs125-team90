import 'package:flutter/material.dart';
import 'package:study_spot_locator/constants.dart';


class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  String _errMsg = "";

  final Color fieldFillColor = lightPrimaryColor;
  final Color buttonColor = darkPrimaryColor;
  final double borderRadius = 25.0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Stack(
          children: [
            Align(
              alignment: Alignment.bottomRight,
              child: Image.asset(
                'assets/anteater.png',
                fit: BoxFit.contain,
                height: 160,
              ),
            ),
            Align(
              alignment: Alignment.bottomLeft,
              child: Padding(
                padding: const EdgeInsets.only(left: 8.0),
                child: Image.asset(
                  'assets/anttrail.png',
                  fit: BoxFit.contain,
                  height: 120,
                ),
              ),
            ),


            Align(
              alignment: Alignment.topCenter,
              child: ConstrainedBox(
                constraints: const BoxConstraints(
                  minWidth: 260,
                ),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 40),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.start,
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      const SizedBox(height: 150,),
                      const Text(
                        "Study Spot Locator",
                        style: primaryTitleStyle
                      ),
                      const SizedBox(height: 25, width: 120,),
                      SizedBox(
                        width: 260,
                        child: Column(
                          children: [
                          _buildTextField("Username", _usernameController, false),
                          const SizedBox(height: 12, width: 120,),
                          _buildTextField("Password", _passwordController, true),
                          if (_errMsg.isNotEmpty)
                            Padding(
                              padding: const EdgeInsets.only(top: 8.0),
                              child: Text(_errMsg, style: primaryErrorStyle),
                            ),
                            
                          const SizedBox(height: 15),
                          
                          Align(
                            alignment: Alignment.centerRight,
                            child: SizedBox(
                              width: 120,
                              height: 30,
                              child: ElevatedButton(
                                onPressed: () {
                                  if (_usernameController.text == "username" && 
                                      _passwordController.text == "password") {
                                    Navigator.pushReplacementNamed(context, '/mainscreen');
                                  } else {
                                    setState(() => _errMsg = "Login Failed");
                                  }
                                },
                                child: const Text("Login"),
                              ),
                            ),
                          ),
                
                          ],
                        ),
                      ),
                      
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTextField(String hint, TextEditingController controller, bool isObscure) {
    return SizedBox(
      width: 260,
      child: TextField(
        controller: controller,
        obscureText: isObscure,
        decoration: InputDecoration(
          hintText: hint,
        ),
      ),
    );
  }  
}