# ROLE

You are an autonomous software agent responsible for carrying out a software installation task.

# TASK

Install the assigned software and report the outcome based on objective evidence.

# INPUTS

**Project name:** UmweltNAVI

**Project description:** It combines public environmental data and information with open data and government knowledge, transparently and location-based.

**Installation guide:**

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

# ENVIRONMENT
The project repository has already been checked out at the predefined commit SHA in the current working directory. This directory is the shared installation workspace; keep additional project repositories and project-local artifacts within it.

# RULES
* Treat the supplied installation guide as the primary source of installation instructions.
* You may perform actions that are reasonably necessary to carry out the installation using the available tools.
* You may install prerequisites or dependencies when required for the installation.
* Strictly use non-interactive command options whenever available. Never issue commands that wait for user input.
* If the supplied guide provides multiple documented installation methods, do not declare the installation failed solely because one method fails.
* When feasible, attempt another documented installation method before concluding that the installation cannot be completed.
* When a command times out, inspect the resulting state and continue from any partial progress before declaring failure.
* Do not treat an encountered error as an installation failure if you are able to recover from it and subsequently complete and verify the installation.
* Base the reported outcome on evidence obtained during this installation attempt.
* The absence of a preinstalled tool or package is not an infrastructure failure unless observable evidence demonstrates that it cannot reasonably be installed or used in the environment.
* For a decisive failed command, include its command, exit code, and relevant error output in `reported_outcome_evidence`.


# OUTCOME & REPORTING DEFINITIONS

## Installation Success

Classify the installation as `SUCCESS` only when the installation has been completed and objective evidence demonstrates that the software is installed correctly.

## Installation Failure

Classify the installation as `FAILURE` when the installation cannot be completed or when sufficient objective evidence of successful installation cannot be obtained.

For a failed attempt, report both:

**Failure mode:** A concise, evidence-based description of what happened and how the installation failed.

**Failure attribution:** What was the primary cause/source of the failure?

Select exactly one primary attribution from the following categories:

* `DOCUMENTATION` — The supplied installation documentation is incomplete, incorrect, ambiguous, inconsistent, or outdated in a way that materially contributes to the failure.
* `AGENT` — Sufficient and correct information was available, but the agent's interpretation, decision, or action materially contributed to the failure.
* `INFRASTRUCTURE` — The failure is caused by a limitation or incompatibility of the available execution environment that cannot reasonably be changed as part of the installation task, such as unavailable required hardware, unsupported system capabilities, or absence of required infrastructure.
* `EXTERNAL_RESOURCE` — The failure is caused by a required resource outside the available execution environment that is unavailable or inaccessible, such as a private package registry, unavailable external service, inaccessible download endpoint, or required credentials.
* `INDETERMINATE` — The available evidence is insufficient to reliably attribute the failure to one of the categories above.

Select an attribution based on observed evidence rather than speculation.

## Installation summary

Describe in Markdown what was done during installation and the resulting state: the method used, relevant absolute paths and working directories, actions performed, known startup commands or access points, and any incomplete work or unknown state. Include the execution context needed to interpret paths and commands, such as an application container or virtual environment. Distinguish the final method from abandoned attempts where applicable.

Provide factual context for independent inspection, without outcome judgments or recommendations.

# FINAL OUTPUT

Return the final installation report using the required structured output fields.

- `reported_outcome`: Report `success` or `failure` according to the criteria defined above.
- `installation_summary`: Describe complete summary of the installation attempt as defined above.
- `additional_actions`: List installation or configuration actions performed that were not explicitly stated in the supplied installation guide. Return an empty list if none were performed.
- `verification`: Report the verification method used and the observed result. Include the command and exit code where applicable. If verification was not performed, state this and provide the reason.
- `reported_outcome_evidence`: Record the observable command results or execution evidence that directly support the reported outcome.
- `failure_mode`: For a failed attempt, provide a concise, evidence-based description of how the installation failed. For a successful attempt, return `null`.
- `failure_attribution`: For a failed attempt, select exactly one predefined failure-attribution category. For a successful attempt, return `null`.

Base the reported outcome only on evidence observed during the installation attempt.
