# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** UmweltNAVI

**Description:** It combines public environmental data and information with open data and government knowledge, transparently and location-based.

## Supplied installation guide

## Guide: Installation.md

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

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

## Method
Followed the supplied guide: fvm → `fvm use 3.35.7` → Android SDK/toolchain setup → `fvm flutter doctor -v` → `fvm flutter pub get` → flavor build (ni). All work performed in the shared container (root, Ubuntu 22.04.5, WSL2 host, 8 cores, 7.6 GB RAM, KVM present) with project at `/workspace`.

## Setup (per guide)
- **Java 17**: OpenJDK 17.0.20.1 via apt (`/usr/lib/jvm/java-17-openjdk-amd64`), wired with `fvm flutter config --jdk-dir=...` (guide's Quirk).
- **fvm**: 4.3.2 binary installed to `/usr/local/bin/fvm` (GitHub release).
- **Flutter 3.35.7 / Dart 3.9.2**: `fvm use 3.35.7` in `/workspace` created `.fvmrc` and `.fvm/flutter_sdk` → `/root/fvm/versions/3.35.7` (versions match guide exactly).
- **tar shim**: Flutter's cache downloads failed as root on overlayfs (`tar: Cannot change ownership ... Invalid argument`); added `/usr/local/bin/tar` wrapper passing `--no-same-owner`. After that all cache artifacts downloaded.
- **Android SDK** at `/opt/android-sdk` (installed headlessly with cmdline-tools, since Android Studio onboarding is GUI-only): licenses accepted; platform-tools 37.0.1, platforms android-34 + android-36, build-tools 34/35/36, emulator 37.2.12, NDK 27.0.12077973 (the `flutter.ndkVersion`), system image `android-36;google_apis;x86_64`. `ANDROID_HOME` exported in `/root/.bashrc`.
- **Virtual device**: AVD `umweltnavi_avd` (pixel_7, API 36) created via avdmanager; boots with KVM (`sys.boot_completed=1`, adb `emulator-5554  device`).
- **Android Studio** 2026.2.1.8 extracted to `/opt/android-studio`; Flutter doctor detects it via the `.home` marker at `/root/.cache/Google/AndroidStudio2026.2.1.8/.home` (content: `/opt/android-studio`, no trailing newline — required by flutter_tools' isDirectorySync check).

## Verification (`fvm flutter doctor -v`, exit 0)
All four requirements from the guide's "Final Check" pass:
- `[✓] Flutter (Channel stable, 3.35.7 ... Dart 3.9.2)`
- `[✓] Android toolchain (Android SDK 36.0.0)` — Java 17 at configured JDK dir, all licenses accepted
- `[✓] Android Studio (version 2026.2.1.8)`
- `[✓] Connected device` (emulator)
Chrome and Linux-desktop toolchain lines are red but are outside the guide's required list (Android/iOS development focus).

## Dependencies & build (per guide)
- `fvm flutter pub get` → `Got dependencies!` (exit 0).
- Built the `ni` flavor following the repo's `ni_release` run-config: `fvm flutter build apk --flavor ni --dart-define=PARTNER=ni --dart-define=cronetHttpNoPlay=true` → **`/workspace/build/app/outputs/flutter-apk/app-ni-release.apk`** (100.3 MB; aapt: package `wemove.app.bipu`, label "UmweltNAVI Niedersachsen", minSdk 24/target 36; apksigner: verified, CN=UmweltNAVI).
- End-to-end: `adb install -r` on the booted AVD → `Success`; launched `de.wemove.umweltnavi.MainActivity` → process alive (pid 2662) across ~2+ min, `dumpsys activity top` shows `mResumed=true mStopped=false`, no `FATAL EXCEPTION` in logcat, valid PNG screenshot captured (1.4 MB).

## Obstacles encountered and resolved
1. **OOM**: project `android/gradle.properties` sets `-Xmx8G -XX:MaxMetaspaceSize=4G` (12 GB) on a 7.6 GB machine; OOM killer killed the Gradle daemon. Tuned to `-Xmx3G -XX:MaxMetaspaceSize=1G` (only local modification to a tracked file) and stopped the emulator during compilation; rebuild then succeeded.
2. **Release signing**: `android/key.properties` + keystore are gitignored/not committed (required by `buildTypes.release`). Generated a local keystore `android/app/release.keystore` + `android/app/key.properties` (password `umweltnavi123`, alias `umweltnavi`); note `storeFile` resolves relative to `android/app/`.
3. **`assets/keys/`** (gitignored API-key asset declared in pubspec) missing → created placeholder `/workspace/assets/keys/api_keys.json` (`{"api_key": ""}`); `ApiService` wraps key loading in try/catch, so runtime behavior is unaffected.
4. Transient podman-related errors from a PATH-resolved `adb` and one missing backgrounded build log — retried; no lasting effect.

## Startup points for the user
- `cd /workspace && fvm flutter doctor -v` / `fvm flutter pub get`
- Run: `fvm flutter run --flavor ni --dart-define=PARTNER=ni --dart-define=cronetHttpNoPlay=true` (per `.run/ni_debug.run.xml`; do not run without `--flavor`)
- Emulator: `/opt/android-sdk/emulator/emulator -avd umweltnavi_avd` (AVD currently booted headless with the app installed)

## Known state
- Tracked-file change: `android/gradle.properties` (heap tuning); untracked: `.fvmrc`, `.fvm/`, `android/app/key.properties`, `android/app/release.keystore`, `assets/keys/api_keys.json`, build outputs.
- Android Studio installed for the doctor check; its Flutter/Dart IDE plugins (IntelliJ Marketplace step in the guide, GUI-only) were not installed — headless environment.
- The emulator, Gradle daemon, and Kotlin daemon may still be running in the background.

# ENVIRONMENT

You have access to the same container used for installation, including the files and dependencies left by the installation attempt. Each terminal call starts a fresh shell in `/workspace`. Shell-local directory changes, exported variables, and environment activation do not persist between calls. Include any required directory change, environment variables, or activation of an existing environment in each command.

# VALIDATION PROCEDURE

1. Review the guide and installation summary. Use the summary to locate the software and its components, and confirm the installation method, locations, and runtime context through inspection.
2. Identify the expected software behavior described in the guide and select checks appropriate to the resulting installation.
3. Run the checks in the correct directory and runtime environment. If needed, start the installed software within the boundaries below. Prefer evidence of software behavior over file existence alone.
4. Record the commands, observed results, and limitations. Assess the outcome using the definitions below and your own observations.

Distinguish the final installation method from abandoned attempts. Missing files required only by another installation method do not establish failure. A process not already running, or a timed-out or unavailable check, does not by itself establish failure.

# VALIDATION BOUNDARIES

You may inspect files, dependencies, processes and ports, run diagnostic commands, start or run the existing installation, and query local interfaces.

Do not install or update dependencies, build missing artifacts, perform missing setup or migrations, edit files or configuration, or repair the installation. Application startup and normal runtime file creation are permitted only when they do not perform these prohibited actions.

# OUTCOME DEFINITIONS

- `success`: Objective evidence obtained during validation demonstrates that the installation is complete and the software is operational according to the supplied guide.
- `failure`: Objective evidence obtained during validation demonstrates that the resulting installation is incomplete or cannot operate without further installation or repair work.
- `inconclusive`: The evidence is insufficient to establish either success or failure, including when observations are ambiguous or an environmental limitation prevents a reliable assessment.

# FINAL OUTPUT

Return the structured validation report with these three fields:

- `assessed_outcome`: Report `success`, `failure`, or `inconclusive` according to the definitions above.
- `outcome_evidence`: Record observable command results or execution evidence that directly support the assessed outcome. Include the exact command, working directory or runtime context, exit code where available, and relevant output for decisive checks. For an inconclusive assessment, record the observations or execution limitations preventing a decision.
- `assessment_summary`: Explain in detail what you inspected, how you performed validation, and how the observations support your assessment. Include checks that could not be completed, limitations, and unresolved uncertainty.