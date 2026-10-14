Installed the Straßennamen web application (Angular frontend + ASP.NET Core 9 backend) in the /workspace container.

Environment: Ubuntu 22.04, Node.js v22.23.3, npm 10.9.9, .NET SDK 9.0.318 (/usr/share/dotnet, symlinked at /usr/local/bin/dotnet), Docker 29.7.2.

Prerequisites installed (none preinstalled): Node.js via NodeSource; .NET SDK 9 via dotnet-install.sh; libicu70 for .NET globalization.

Frontend (/workspace/src/Frontend/Strassennamen): npm i (742 packages) succeeded; npm run build produced ./dist (exit 0); npm run start served on http://localhost:4200 (HTTP 200). Configured public/configs/config.development.json with endPointUrl http://localhost:5000/api and a keycloak block (realm my-realm, authServerUrl http://localhost:8080/, resource strassennamen). The committed default used a stale "auth" key; the code (app-settings.ts / get-keycloak.config.ts) reads "keycloak", matching the guide.

Backend (/workspace/src/Backend): dotnet restore and dotnet build Lecos.Strassennamen.sln -c Debug succeeded with 0 errors. Configured Lecos.Strassennamen.RestAPI/appsettings.Development.json per the guide. Ran the RestAPI on http://localhost:5000 under ASPNETCORE_ENVIRONMENT=Development; FluentMigrator applied migrations creating 14 tables; Swagger returned HTTP 200.

Infrastructure (Docker): SQL Server 2022 container strassennamen-sql (port 1433, sa password Strassen!Passw0rd); created Strassennamen database. Keycloak 26.0 container strassennamen-keycloak (port 8080, admin/admin); created realm my-realm, public client strassennamen with redirect URIs for 4200/5000, client roles app-access/editor, and testuser (Test1234!) assigned both client roles.

End-to-end: Keycloak token for testuser contained resource_access.strassennamen.roles=[editor,app-access]; GET http://localhost:5000/api/strasse with bearer token returned HTTP 200 (empty JSON array). Unauthenticated requests return 401/403 as designed.

Startup: backend `PATH=$PATH:/usr/share/dotnet dotnet run --project Lecos.Strassennamen.RestAPI --urls http://localhost:5000` (env Development); frontend `npm run start` -> http://localhost:4200; Keycloak http://localhost:8080.

Modified tracked files: backend appsettings.Development.json, frontend public/configs/config.development.json, frontend package-lock.json; new dir Export/. Backend unit tests reported "no test available" (discovery issue) but this did not affect build/runtime verification.