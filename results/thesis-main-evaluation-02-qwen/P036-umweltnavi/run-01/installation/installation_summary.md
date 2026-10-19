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