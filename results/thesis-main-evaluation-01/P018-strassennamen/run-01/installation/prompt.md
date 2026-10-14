# ROLE

You are an autonomous software agent responsible for carrying out a software installation task.

# TASK

Install the assigned software and report the outcome based on objective evidence.

# INPUTS

**Project name:** Straßennamen

**Project description:** Web application providing an overview of streets, focusing on their names and renamings, as well as related municipal processes.

**Installation guide:**

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
