# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** Straßennamen

**Description:** Web application providing an overview of streets, focusing on their names and renamings, as well as related municipal processes.

## Supplied installation guide

## Guide: Installation.md

# Getting Started

## Keycloak

Es wird eine laufende Instanz von [Keycloak](https://www.keycloak.org/getting-started/getting-started-docker) für die Authentifizierung benötigt.

Es muss ein Client (vorzugsweise "strassennamen") eingerichtet sein, auf den Frontend wie Backend zugreifen können.

Folgende Rollen sind zwingend vorausgesetzt:

- app-access (Diese Rolle gibt die Anwendung für den Nutzer frei)
- editor (Diese Rolle gibt Bearbeitungsrecht frei)

### Client Konfiguration

Des Weiteren muss der Client auf Frontend und Backend konfiguriert werden:

#### Allgemeine Einstellungen

`Client-ID` muss zu den Einstellungen im Backend und Frontend passen.

#### Zugriffseinstellungen

`Root URL` und `Home-URL` müssen die URL des Frontends sein.

`Valid redirect URIs` müssen Backend und Frontend eingetragen werden. Diese enden immer mit einem *.

Beispiel:

- http://localhost:4200/*
- http://localhost:5000/*

`Valid post logout redirect URIs` muss immer das Frontend sein und mit einem * enden.

Beispiel:

- http://localhost:4200/*

`Web Origins` und `Admin URL` muss das Frontend angegeben werden.

#### Protokolleinstellungen

Authentifizierungsablauf muss folgende aktiviert werden:

* Standard-Flow
* Direct access grants
* Implicit flow

Die Client-Authentifizierung und die Autorisierung dürfen nicht aktiviert sein.

Der Rest unter `Protokolleinstellungen` sollte standard sein.

## Frontend

Das Frontend verwendet [Angular](https://angular.dev/). Über den Konsolen-Befehl `npm i`, im Verzeichnis des Frontends `./src/Frontend/Strassennamen`, kann die App installiert werden.

Im Ordner `./src/Frontend/Strassennamen/configs/config.development.json` muss die `endPointUrl` zum Backend angegeben werden.

In `keycloak` müssen die Zugriffsdaten von keykloak hinterlegt werden.

`resource` bezieht sich hierbei auf den Client im Keycloak.

Beispiel Konfiguration:

```json
{
  "endPointUrl": "http://localhost:5000/api",
  "keycloak": {
    "realm": "my-realm",
    "authServerUrl": "http://localhost:8080/",
    "resource": "strassennamen"
  }
}
```

**Achtung, die URL zum Frontend, muss im Backend als CORS Konfiguration hintergelegt sein.**

## Backend

Hierzu wird eine Entwicklungsumgebung benötigt. Die Entwicklung entstand mit Rider.

Kann aber auch mit [Visual Studio Community](https://visualstudio.microsoft.com/de/vs/community/) oder Vergleichbarem gestartet werden.

Zuerst ist eine Datenbank mit SQL vonnöten. Diese muss zu [Entity Framework](https://github.com/dotnet/efcore) kompatibel sein.

Zum Einsatz kam eine MS-SQL Datenbank.

Lokal sollte eine [SQL Server Express LocalDB](https://learn.microsoft.com/de-de/sql/database-engine/configure-windows/sql-server-express-localdb) ausreichen.

Im Ordner `./src/Backend/appsettings.Development.json` wird das Backend konfiguriert. Wichtig sind dabei vor allem, die Angabe der Keycloak Konfiguration, der CorsOrigins und den ConnectionStrings.

Beispiel Konfiguration:

```json
{
  "Serilog": {
    "Using":  [ "Serilog.Sinks.File" ],
    "MinimumLevel": {
      "Default": "Debug",
      "Override": {
        "Microsoft.AspNetCore": "Information",
        "Microsoft.EntityFrameworkCore": "Warning",
        "System.Net.Http": "Warning"
      }
    },
    "WriteTo": [
      {
        "Name": "File",
        "Args": {
          "path": "Logs/log-.txt",
          "rollingInterval": "Day",
          "retainedFileCountLimit": "15"
        }
      }
    ]
  },
  "Logging": {
    "LogLevel": {
      "Default": "Debug",
      "Microsoft.EntityFrameworkCore.Database.Command": "Warning"
    }
  },
  "Keycloak": {
    "Realm": "my-realm",
    "AuthServerUrl": "http://localhost:8080/",
    "SslRequired": "none",
    "Resource": "strassennamen",
    "PublicClient": true,
    "VerifyTokenAudience": false,
    "ConfidentialPort": 0,
    "ClientName": "strassennamen"
  },
  "CorsOrigins": [
    "http://localhost:4200"
  ],
  "ConnectionStrings": {
    "DB": "Server=(localdb)\\MSSQLLocalDB;Database=Strassennamen;Integrated Security=true"
  },
  "Jobs": {
    "Heartbeat": {
      "Active": true,
      "CronSchedule": "0 0/5 * 1/1 * ? *"
    },
    "XmlExportStrassen": {
      "Active": true,
      "CronSchedule": "0 0 1 1/1 * ? *",
      "FilePath": "Export/strassen.xml",
      "FilterStrassenStatus": "Aktiv"
    }
  }
}
```

*Anmerkungen*

- CorsOrigins:
    - hier sollte die fronend domain hinterlegt werden, damit das backend den Zugriff erlaubt
- Serilog:
    - path angabe wohin die log files geschrieben werden sollen. schreibrechte sollten vorhanden sein
- Jobs
    - Heartbeat: Sorgt dafür, dass der XmlExportStrassen 1x beim Start sofort ausgeführt wird
    - XmlExportStrassen:
        - Kann mit Intervall die Straßen zu einer XML-Datei ausliefern
        - Der Filepath muss entsprechend angepasst werden und Zugriff (z.B. anderer Netzwerkpfad) sollte vom Webserver aus gewährleistet sein
        - FilterStrassenStatus: Gib an welche Straßen exportiert werden wollen. Default Aktiv
            - Status-angaben: Aktiv, Inaktiv, Unbekannt, InBearbeitung. null
            - null bedeutet, dass alle Straßen ausgegeben werden

**Sollte das Frontend nicht unter `http://localhost:4200` laufen, muss dies unter `CorsOrigins` angepasst werden.**

# Build and Start

## Backend

Hierzu muss je nach Entwicklungsumgebung, das Projekt `Lecos.Strassennamen.RestAPI` als Startprojekt festgelegt werden.

## Frontend

Über den Konsolen-Befehl `npm run start` kann das Frontend gestartet werden.

Da eine Authentifizierung immer dringend vonnöten ist, wird die Anwendung zuerst auf den Keycloak-Server weiterleiten, um sich anzumelden.

Bitte darauf achten, dass im Keycloak die entsprechenden Urls hinterlegt sind, damit Frontend und Backend zurückgeleitet werden können.

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

Installed the Straßennamen web application (Angular frontend + ASP.NET Core 9 backend) in the /workspace container.

Environment: Ubuntu 22.04, Node.js v22.23.3, npm 10.9.9, .NET SDK 9.0.318 (/usr/share/dotnet, symlinked at /usr/local/bin/dotnet), Docker 29.7.2.

Prerequisites installed (none preinstalled): Node.js via NodeSource; .NET SDK 9 via dotnet-install.sh; libicu70 for .NET globalization.

Frontend (/workspace/src/Frontend/Strassennamen): npm i (742 packages) succeeded; npm run build produced ./dist (exit 0); npm run start served on http://localhost:4200 (HTTP 200). Configured public/configs/config.development.json with endPointUrl http://localhost:5000/api and a keycloak block (realm my-realm, authServerUrl http://localhost:8080/, resource strassennamen). The committed default used a stale "auth" key; the code (app-settings.ts / get-keycloak.config.ts) reads "keycloak", matching the guide.

Backend (/workspace/src/Backend): dotnet restore and dotnet build Lecos.Strassennamen.sln -c Debug succeeded with 0 errors. Configured Lecos.Strassennamen.RestAPI/appsettings.Development.json per the guide. Ran the RestAPI on http://localhost:5000 under ASPNETCORE_ENVIRONMENT=Development; FluentMigrator applied migrations creating 14 tables; Swagger returned HTTP 200.

Infrastructure (Docker): SQL Server 2022 container strassennamen-sql (port 1433, sa password Strassen!Passw0rd); created Strassennamen database. Keycloak 26.0 container strassennamen-keycloak (port 8080, admin/admin); created realm my-realm, public client strassennamen with redirect URIs for 4200/5000, client roles app-access/editor, and testuser (Test1234!) assigned both client roles.

End-to-end: Keycloak token for testuser contained resource_access.strassennamen.roles=[editor,app-access]; GET http://localhost:5000/api/strasse with bearer token returned HTTP 200 (empty JSON array). Unauthenticated requests return 401/403 as designed.

Startup: backend `PATH=$PATH:/usr/share/dotnet dotnet run --project Lecos.Strassennamen.RestAPI --urls http://localhost:5000` (env Development); frontend `npm run start` -> http://localhost:4200; Keycloak http://localhost:8080.

Modified tracked files: backend appsettings.Development.json, frontend public/configs/config.development.json, frontend package-lock.json; new dir Export/. Backend unit tests reported "no test available" (discovery issue) but this did not affect build/runtime verification.

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