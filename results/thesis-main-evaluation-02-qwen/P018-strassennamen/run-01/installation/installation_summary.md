## What was done

**Environment:** Ubuntu 22.04 container at `/workspace` (repo checked out at the pinned commit). Docker 29.7.2 with daemon available; Node.js, npm, and dotnet were absent and were installed as prerequisites.

### Prerequisites installed (not in guide, required)
- **Node.js 22.23.3 / npm 10.9.9** via NodeSource apt repo (Angular 21 frontend needs Node ≥20.19).
- **.NET SDK 9.0.319** via the official `dotnet-install.sh` script to `/usr/local/dotnet` (backend targets net9.0), symlinked to `/usr/local/bin/dotnet`. `libicu74` installed (SDK refuses to start without ICU; app uses `de-DE` culture so invariant mode was not used).

### Keycloak (port 8080) — per guide
- Ran `quay.io/keycloak/keycloak:26.4.6` in `start-dev` mode (`docker run -d --name keycloak -p 8080:8080 -e KC_BOOTSTRAP_ADMIN_USERNAME=admin -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin`), started on http://localhost:8080 (ready after ~40s).
- Created realm `my-realm` and client `strassennamen` via the Keycloak Admin REST API with exactly the guide's settings: `rootUrl`/`baseUrl`/`adminUrl` = `http://localhost:4200/`, redirect URIs `http://localhost:4200/*` and `http://localhost:5000/*`, web origins `http://localhost:4200/*`, post-logout redirect `http://localhost:4200/*` (stored as client attribute `post.logout.redirect_uris` — the Keycloak 26 API location), Standard-Flow + Direct access grants + Implicit flow enabled, public client (no client authentication, no service accounts/authorization).
- Created the two required client roles `app-access` and `editor` on the client.
- Created test user `user1` (password `user1pass`) with both roles assigned; verified a direct-access-grant token contains `resource_access.strassennamen.roles = [editor, app-access]`.

### Frontend (http://localhost:4200)
- `cd /workspace/src/Frontend/Strassennamen && npm i` → "added 742 packages".
- Wrote `public/configs/config.development.json` per the guide's example: `endPointUrl: http://localhost:5000/api`, `keycloak: {realm: my-realm, authServerUrl: http://localhost:8080/, resource: strassennamen}`. (The committed file pointed to `https://example.com` and used a stale `auth` key; the app code and the guide both expect the `keycloak` key, so it was updated to the guide's shape.)
- `npm run start` (Angular dev server) → "Application bundle generation complete", serving at http://localhost:4200 (HTTP 200, `<title>Leipziger Strassennamen</title>`; config file served correctly at `/configs/config.development.json`).

### Backend (http://localhost:5000)
- Database: the guide requires an Entity-Framework-compatible SQL database ("Zum Einsatz kam eine MS-SQL Datenbank"; LocalDB is Windows-only), so SQL Server 2022 was run via Docker (`mcr.microsoft.com/mssql/server:2022-latest`, port 1433, SA password `Strassen#2024`) and database `Strassennamen` created.
- Wrote `/workspace/src/Backend/Lecos.Strassennamen.RestAPI/appsettings.Development.json` following the guide's example: Keycloak section (`Realm: my-realm`, `AuthServerUrl: http://localhost:8080/`, `SslRequired: none`, `Resource: strassennamen`, `PublicClient: true`, `VerifyTokenAudience: false`, `ClientName: strassennamen`), `CorsOrigins: ["http://localhost:4200"]`, `ConnectionStrings.DB` pointing at the SQL Server container, Jobs (Heartbeat active, XmlExportStrassen active with `Export/strassen.xml`), Serilog file sink to `Logs/`.
- `dotnet build Lecos.Strassennamen.RestAPI.csproj` → "Build succeeded, 0 Errors" (9 pre-existing warnings).
- Started with `ASPNETCORE_ENVIRONMENT=Development ASPNETCORE_URLS=http://localhost:5000 dotnet run` → "Now listening on: http://localhost:5000", "Application started". FluentMigrator migrations ran at startup, creating 14 tables (Strassen, Vorgaenge, Beschluesse, etc.) in the `Strassennamen` database.
- Quartz jobs ran: `XmlExportStrassen` fired once at startup and wrote `Export/strassen.xml` (`<Strassenverzeichnis />`, empty since no streets exist yet).

### Final verified state (all live in the container)
| Component | Port | Evidence |
|---|---|---|
| Keycloak (docker `keycloak`) | 8080 | HTTP 302 root; admin APIs working |
| SQL Server 2022 (docker `mssql`) | 1433 | `SELECT 1` ok; 14 tables in `Strassennamen` |
| Backend (dotnet, RestAPI) | 5000 | Swagger 200; API auth verified |
| Frontend (ng serve) | 4200 | HTTP 200, correct title and config served |

Auth end-to-end: `GET /api/Strasse` without token → 401; with fresh `user1` bearer token → **200** `[]`; CORS preflight and real requests from origin `http://localhost:4200` return `Access-Control-Allow-Origin: http://localhost:4200` with credentials.

## Notes / doc deviations handled
- Guide says frontend config is at `./src/Frontend/Strassennamen/configs/config.development.json`; the repo's actual file is `./src/Frontend/Strassennamen/public/configs/config.development.json` (frontend loads `/configs/config.development.json` from the public root).
- Guide says backend config is at `./src/Backend/appsettings.Development.json`; actual file is `./src/Backend/Lecos.Strassennamen.RestAPI/appsettings.Development.json`.
- LocalDB (guide's suggested local DB) does not exist on Linux; the guide explicitly allows any EF-compatible SQL database and states MS-SQL was used, so SQL Server 2022 in Docker was used.
- Keycloak admin API in 26.x rejects legacy field names (`validPostLogoutRedirectUris` etc.), so the client was configured with the current schema (values equivalent to the guide's UI settings).

## Startup commands (for future sessions)
- Keycloak: `docker start keycloak`; SQL: `docker start mssql`
- Backend: `cd /workspace/src/Backend/Lecos.Strassennamen.RestAPI && ASPNETCORE_ENVIRONMENT=Development ASPNETCORE_URLS=http://localhost:5000 dotnet run`
- Frontend: `cd /workspace/src/Frontend/Strassennamen && npm run start`
- Logins: Keycloak admin `admin`/`admin` (master); app user `user1`/`user1pass` (realm `my-realm`, client `strassennamen`, roles `app-access`+`editor`)