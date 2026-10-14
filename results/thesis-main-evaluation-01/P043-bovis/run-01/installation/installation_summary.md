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