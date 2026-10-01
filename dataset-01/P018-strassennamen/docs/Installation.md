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
