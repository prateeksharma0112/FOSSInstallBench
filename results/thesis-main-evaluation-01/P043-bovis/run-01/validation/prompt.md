# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** BoVis

**Description:** BoVis drill column visualization

## Supplied installation guide

## Guide: Installation.md

# BoVis – Bohrsäulenvisualisierung

## Schnellstart

```bash
git clone https://gitlab.opencode.de/oc000047244955/bovis.net.git
cd bovis.net/src/Bovis.Web
cp local.json.in local.json
# local.json anpassen: Datenbankverbindung eintragen
dotnet run -- server
```

Eine Installationsanleitung für die Bereitstellung auf einem Webserver (z.B. IIS, Apache, Nginx) befindet sich in [docs/INSTALL.adoc](docs/INSTALL.adoc)

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

Installed and ran BoVis (.NET 8 Blazor web app) from source in /workspace.

Environment context: Ubuntu 22.04, root user, shared install workspace /workspace (repo already checked out at commit cd2c942).

Prerequisites installed (not preinstalled):
- .NET 8 SDK 8.0.425 installed via https://dot.net/v1/dotnet-install.sh --channel 8.0 --install-dir /usr/share/dotnet; symlinked to /usr/bin/dotnet.
- apt packages: libicu70, libssl3, zlib1g (required to run dotnet) and libfontconfig1 (required by SkiaSharp / BohrlochRenderer). libfontconfig1 resolved a DllNotFoundException for libSkiaSharp.

Method (from guide "Schnellstart"):
1. cd /workspace/src/Bovis.Web
2. cp local.json.in local.json
3. dotnet restore (success) then dotnet build (success, 0 errors)
4. dotnet run -- server

Default method outcome: with the guide's sample local.json (sqlite:bohris.db, default DataBackend=Bohris), the app failed to start with Microsoft.Data.Sqlite.SqliteException 'no such table: L_FARBE' because the sample SQLite data DB has no Bohris schema (the real Bohris data lives in an external Hadoop/Oracle DB). The repository's own src/Bovis.Web/README.md documents the DataBackend setting and LBEG backend. Configuring local.json with "DataBackend": "LBEG" let the service start cleanly.

Final working method: local.json at /workspace/src/Bovis.Web/local.json containing ConnectionStrings DataConnection=sqlite:bohris.db, ConfigConnection=sqlite:config.db, DataBackend=LBEG; started with `dotnet run --no-build -- server` from /workspace/src/Bovis.Web.

Access point: http://localhost:5195 (chosen by Properties/launchSettings.json "http" profile under ASPNETCORE_ENVIRONMENT=Development; appsettings.json Kestrel setting of 18080 is overridden by launch profile when using `dotnet run`).

Artifacts created: /workspace/src/Bovis.Web/config.db (SQLite config DB, schema 001) and /workspace/src/Bovis.Web/bohris.db (empty data DB). App base path is /workspace/src/Bovis.Web/bin/Debug/net8.0.

Unknown/incomplete: No real borehole data is available; to visualize actual data the DataConnection must point to a real Bohris/LBEG database. The app is only bound to localhost:5195 with no reverse proxy/systemd integration (docs/Install.adoc deployment steps were not required for the quickstart install).

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