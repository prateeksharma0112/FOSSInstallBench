## UmweltNAVI — Flutter app installation

**Context:** Ubuntu 22.04 container, repo checked out at `/workspace` (Flutter/Dart project `umwelt_navi_app`, version 2.8.0+1). No tooling was preinstalled (no flutter, dart, fvm, java).

**Method used (final, successful):**
1. **Flutter SDK 3.35.7** — fetched the official stable Linux tarball from `storage.googleapis.com/flutter_infra_release`, verified SHA-256 `146df531f9ac6a11a918013c1a70faafc053d4811c8cb69a413fd70748d51c3d`, extracted to `/opt/flutter`. `flutter --version` reports Flutter 3.35.7 / Dart 3.9.2, matching the guide.
2. **Java 17** — `apt-get install openjdk-17-jdk-headless` (openjdk 17.0.20.1); configured via `flutter config --jdk-dir=/usr/lib/jvm/java-17-openjdk-amd64`.
3. **Android SDK** — downloaded commandlinetools-linux-11076708 to `/opt/android-sdk/cmdline-tools/latest`, ran `sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"`; registered via `flutter config --android-sdk /opt/android-sdk`. Gradle additionally auto-installed NDK 27.0.12077973 and platforms 29/31/35 during build.
4. **Linux desktop deps** — installed clang, cmake, ninja-build, pkg-config, libgtk-3-dev (so `flutter doctor` Linux toolchain passes).
5. **Dependencies** — `flutter pub get` in `/workspace`; resolved all pubspec packages.
6. **Repo-local generated files (not in VCS, produced from CI secrets in real pipelines):**
   - `android/key.properties` + `android/app/debug-keystore.jks` (debug keystore); required because `android/app/build.gradle` evaluates `signingConfigs.release` unconditionally and failed with `path='null'` without it.
   - `assets/keys/api_keys.json` placeholder (`{}`); the directory is a declared pubspec asset, and the build failed with "unable to find directory entry in pubspec.yaml: /workspace/assets/keys/" without it.
7. **Build verification** — `flutter build apk --debug --flavor ni --dart-define=PARTNER=ni --dart-define=cronetHttpNoPlay=true` completed: `✓ Built build/app/outputs/flutter-apk/app-ni-debug.apk`.

**Final state:** Working Flutter toolchain and Android SDK; project dependencies resolved; a valid debug APK exists at `/workspace/build/app/outputs/flutter-apk/app-ni-debug.apk` (201,557,558 bytes). `flutter doctor` shows Flutter ✓, Android toolchain ✓, Linux toolchain ✓, network ✓. Env exports persisted to `/etc/profile.d/flutter.sh`; setup notes written to `/workspace/AGENTS.md`.

**Known limitations / environment notes:** Android Studio (GUI) and Xcode (iOS-only) cannot be installed headless; the guide lists them as doctor requirements, but they are not required to build/verify the Android app in this Linux container. `flutter doctor` still reports Android Studio and Chrome as missing. A real `assets/keys/api_keys.json` with production API keys is required for live API calls — only a placeholder was created. `flutter analyze` reports 96 info-level lints and 0 errors.

**Abandoned attempts:** Used direct SDK tarball instead of `fvm` (fvm not installed; guide says it is "strongly recommended", not required) — same Flutter 3.35.7 version achieved. Two initial build attempts failed (missing key.properties; missing assets/keys/) and were recovered by generating those files.