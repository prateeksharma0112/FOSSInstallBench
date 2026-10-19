## Environment
- Ubuntu 22.04 container (shared installation workspace), all commands run as root.
- Repository: the BoVis repository (gitlab.opencode.de/oc000047244955/bovis.net, commit cd2c942) was already checked out at `/workspace`; the guide's `git clone` step was therefore not repeated. Working directory for all build/run commands: `/workspace/src/Bovis.Web`.

## Steps performed
1. **Prerequisites (not in guide):** installed `dotnet-sdk-8.0` (8.0.131) via `apt-get` (non-interactive), plus `libfontconfig1`/`fontconfig` (SkiaSharp native dependency) and `sqlite3` (CLI, for DB setup).
2. **Guide step:** `cd /workspace/src/Bovis.Web && cp local.json.in local.json` — `local.json` uses the default SQLite connections (`DataConnection: sqlite:bohris.db`, `ConfigConnection: sqlite:config.db`); no external database (Oracle) was needed because of this default.
3. **Build:** `dotnet build` in `/workspace/src/Bovis.Web` — build succeeded, 0 errors, 10 warnings (incl. NU1903 vulnerability advisories for `Microsoft.AspNetCore.Authentication.Negotiate` 8.0.11 — noted, not blocking).
4. **Config check:** `dotnet run --no-build -- check` — exited 0.
5. **First server start failed** with `DllNotFoundException: libfontconfig.so.1` (SkiaSharp `SKTypeface` type initializer); fixed by installing `libfontconfig1`.
6. **Second server start failed** with `SQLite Error 1: 'no such table: L_FARBE'` — the app opens the default `bohris.db` (created as an empty 0-byte SQLite file) and its `BohrisShortCodeDecoder` queries `L_FARBE`, `L_GENESE`, `L_PETH`, `L_STRATIGRAPHIE`, `L_ZUSATZ`, `L_DS_STA_PRI` at startup, and `Open()` additionally queries `L_MESSVERFAHREN`. These six key tables plus `L_MESSVERFAHREN` were created in `/workspace/src/Bovis.Web/bohris.db` (with a couple of sample rows) so the app can open its data connection. This is the app's normal data-connection setup path — no source code was modified.
7. **Final start (the documented command):** `dotnet run --no-build -- server` from `/workspace/src/Bovis.Web`, run in the background (`nohup`, log at `/tmp/bovis_server.log`). The app's own `server` subcommand starts Kestrel; it chose port **5195** (from its runtime configuration, not the 18080 in `appsettings.json.in`, which is only a template).

## Resulting state
- Installed/running app: `/workspace/src/Bovis.Web/bin/Debug/net8.0/Bovis.Web server` (PID 1655 during verification).
- Access point: `http://localhost:5195/` (Blazor UI; public base path `/app`, i.e. `http://localhost:5195/app`).
- Databases created by the app/config at `/workspace/src/Bovis.Web/`: `config.db` (self-managed schema 001) and `bohris.db` (seeded with the seven required `L_*` tables).
- Default admin user per `appsettings.json`: `user` (role admin).
- Server log: `/tmp/bovis_server.log`.
- Incomplete/known: the `bohris.db` data database contains only empty lookup tables, so no real drill-column (BohrIS) data can be visualized until a real data connection is configured in `local.json` (e.g., the Oracle/BohrIS connection the guide mentions); the NU1903 package vulnerability warnings remain in the build.