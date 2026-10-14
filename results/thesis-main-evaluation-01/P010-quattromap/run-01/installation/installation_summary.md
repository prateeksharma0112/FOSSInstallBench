## QuattroMap installation

**Working directory / repo:** `/workspace` (git commit 24041c0, "Update .gitlab-ci.yml"). This is the shared installation workspace on Ubuntu 22.04.

**Prerequisite — Node.js:**
- The environment had no `node`/`npm` (`exit code 127`). The Ubuntu 22.04 apt candidate is only `nodejs 12.22.9`, too old for the project's toolchain.
- Added the NodeSource `setup_20.x` repo and ran `apt-get install -y nodejs`, yielding `node v20.20.2` and `npm 10.8.2`.
- Downloaded the NodeSource setup script from `https://deb.nodesource.com/setup_20.x` (a non-apt-source registry), so this step is a non-guide prerequisite action.

**Method used (per the guide's Develop section):**
1. `npm install` in `/workspace` → `added 403 packages` (exit 0). Emitted EBADENGINE warnings: `webpack-dev-server@6.0.0` requires `node >= 22.15.0`, `p-retry@8.0.0` requires `node >=22`; these were warnings only and did not block execution.
2. `npm run build` (`webpack`) → `webpack 5.110.3 compiled with 4 warnings` (exit 0). Warnings are performance/size and a maplibre dynamic-require notice, not errors. Output produced at `/workspace/dist/`: `bundle.js` (~1.29 MB), `index.html`, `oss-licenses.json`, `img/`, `vendor/`.
3. `npm start` (`webpack serve`) → dev server compiled successfully (`152 modules`) and served the app.

**Verification (evidence):**
- `curl http://localhost:8080/` → HTTP 200, `<title>QuattroMap</title>`, 9372 bytes.
- `curl http://localhost:8080/bundle.js` → HTTP 200, 1,356,256 bytes.
- Dev server log: `[webpack-dev-server] Project is running at: ... http://localhost:8080/`.

**Access points / startup commands:**
- Production build served from `/workspace/dist` (any static server).
- Dev server: `npm start` in `/workspace`, default `http://localhost:8080/` (one run bound `8081` because a previous instance still held `8080`).

**Cleanup:** All webpack/dev-server processes started during verification were terminated.

**Unknown/incomplete:** None material. The only caveat is the Node engine mismatch warning from `webpack-dev-server@6.0.0` (declares Node >= 22.15.0) while the installed runtime is Node 20; build and dev server nonetheless functioned and served correctly.