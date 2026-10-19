## Installation: QuattroMap

**Environment:** Ubuntu 22.04 container, shared workspace at `/workspace` (repo already checked out at commit `24041c0`). Node.js/npm were NOT preinstalled.

### Method (final)
Followed the guide's "Develop" section: `npm install` + `npm start` (dev server) and `npm run build`, after first installing the Node.js prerequisite.

### Steps performed
1. **Prerequisite (not in guide):** Installed Node.js 20.20.2 / npm 10.8.2 via the NodeSource apt repository (`curl -fsSL https://deb.nodesource.com/setup_20.x | bash` then `apt-get install -y nodejs`), because the project's webpack 5.110 / webpack-dev-server 6 require Node >= 18 and Ubuntu 22.04's repo node is older.
2. `cd /workspace && npm install` — exit 0; 283 packages in `/workspace/node_modules` (npm reported 15 pre-existing audit vulnerabilities, non-blocking).
3. `cd /workspace && npm run build` — exit 0; webpack 5.110.3 compiled with warnings only (bundle size / dynamic-require notices, non-fatal). Build output in `/workspace/dist/`: `index.html`, `bundle.js` (~1.24 MiB), `vendor/maplibre/`, `img/`, `oss-licenses.json`.
4. `cd /workspace && npm start` (webpack-dev-server, per webpack.config.js with no explicit port → default 8080, matching the guide) — compiled successfully; verified serving then stopped the server by PID so port 8080 is now free.

### Access points / startup
- Dev server: `cd /workspace && npm start` → http://localhost:8080/
- Production build: `/workspace/dist/` (static, servable by any web server); `npm run deploy` publishes to gh-pages (not run).
- Runtime configuration lives in `/workspace/src/config.json` (center, zoom, maps, crosshair, layers) per the guide.

### Final state
Node 20.20.2 + npm 10.8.2 installed system-wide; `/workspace/node_modules` and `/workspace/dist/` populated; no dev server currently running. No source files were modified.