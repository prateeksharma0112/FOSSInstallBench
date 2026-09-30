# 🌍 UmweltNAVI
The app provides a rich overview of user’s surrounding area as well as the whole of Germany, including environmental conditions, natural habitats, points of interest and more. The app is written in Dart with [Flutter](https://flutter.dev/). Please make sure to have all the required tooling and configurations set up before starting.

## 📍 Setup
To ensure a smooth onboarding, use the versions of the tooling below:

* Flutter: 3.35.7
* Dart: 3.9.2
* Java: 17

However, [Flutter Version Manager](https://fvm.app/) (fvm) is strongly recommended to manage different versions of Flutter. Follow the official documentation and install it on your device. After the installation, initialize Flutter SDK in the root directory with the following command:

```
fvm use 3.35.7
```

This command creates a symlink to the Flutter SDK in the root directory. You might need to configure the path to the initialized Flutter SDK in your desired IDE. The following section is the demonstration of further setup for IntelliJ IDEA.

### 💡 IntelliJ IDEA or Android Studio

* Download `Flutter` and `Dart` Pugins from IntelliJ Marketplace.
* After the installation, head to Flutter configuration and change the Flutter SDK path to the initialized Flutter SDK in the root directory, such as `/Users/user/Documents/bipu-app-flutter/.fvm/flutter_sdk`.
* Switch to Dart configuration. The path should be automatically set. When not, change it to the initialized Dart SDK, such as `/Users/user/Documents/bipu-app-flutter/.fvm/flutter_sdk/bin/cache/dart-sdk`.

### 💡 Android Studio
To debug on androidOS, you must have Android Studio installed. During the onboarding, you will be guided to install the relevant components. If not, head to the **Settings > Android SDK** to choose the rest. The following components are required:

* Android SDK Platform 34 or above.
* Android SDK Platform-Tools.
* Android Emulator, and with a virtual device ready in Device Manager.

Make sure your virtual device can be started and connected to the IDE.

### 🚦 Final Check
Use Flutter commandline to check if your development environment is correctly set up:

```
fvm flutter doctor -v
```

You must fulfill at least the following requirements for development:
* Flutter
* Android toolchain
* Android Studio
* Xcode (for iOS on a Mac)

#### Quirks
* You might be prompted to accept the usage license.
* For iOS, you must additionally have `cocapod` installed.
* Under Android toolchain, Java binary must be pointed to a directory with java version 17. To change the path, use:

```
fvm flutter config --jdk-dir=<DIRECTORY>
```


## 📍 Development

Before starting the debug mode in a virtual device, all dependencies defined in `pubspec.yaml` must be installed. Use the following command:
```
fvm flutter pub get
```

All line errors should be resolved afterward. To debug the app for iOS, you must possess a MacBook.

### 🐛 Start Debugging
You **must** select a [flavor](https://docs.flutter.dev/deployment/flavors) (profiling) to start the debugging mode. The run configs are already set for IntelliJ IDEA, Android Studio and VS Code.

You should see the configurations available with different partner annotations in UI such as `ni_debug`, `ni_release`, `sh_debug`. The annotation is formulated using the partner as the leading and the mode after the underline, such as `<partner>_<mode>` -> `rp_debug`.

`ni_release` for instance, the app will be built with the production settings, which can fully represent real-life usage on an emulator.

!! Do not use the `main.dart` to start debugging, because it does not point to a flavor.

### 💡 Useful Commandlines
To clean up the build cache:
```
fvm flutter clean
```

To clean up the pub cache (dependency cache):
```
fvm dart pub cache clean
```
