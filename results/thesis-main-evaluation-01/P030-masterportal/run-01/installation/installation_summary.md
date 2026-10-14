## Method
Masterportal (v3.26.1, commit 410dc25) was installed from the checked-out source in `/workspace` by installing Node.js, project npm dependencies, and building the portal bundle, then verifying it via a local web server.

## Steps and paths
- **Node.js prerequisite:** No Node runtime was present. Downloaded `node-v22.20.0-linux-x64.tar.xz` from nodejs.org, extracted to `/opt/node`, symlinked `node`, `npm`, `npx` into `/usr/local/bin`. Result: `node v22.20.0`, `npm 10.9.3` (matches the project's `engines` constraint).
- **Dependencies:** `cd /workspace && npm install --no-audit --no-fund` → "added 842 packages in 31s", exit 0. Uses the npmjs.org registry specified in the project's `.npmrc`.
- **Build:** The documented `npm run build` wrapper (`devtools/tasks/viteBuild.js`) is interactive (readline prompt for portal folder). It was invoked with piped stdin (defaulted to `portal`) and, for reliability, the underlying command was also run directly non-interactively: `npx cross-env PORTAL_FOLDER=portal npx vite build --config devtools/vite.config.js`. Build completed: `✓ built in 24.22s`, exit 0.
- **Artifacts:** `/workspace/dist/` contains the example portals `auto/`, `basic/`, `master/` (each with `index.html`, `config.js`, `config.json`, `resources/`), plus `mastercode/3_26_1_410dc25_git_last_commit_at_2026-09-23__10-05-39/{js,css,img,locales}`. `/workspace/dist/portal/{auto,basic,master}` also present.

## Access points / startup commands
- Production build output is served statically from `/workspace/dist`; entry example: `dist/basic/index.html` (references `../mastercode/<version>/js/masterportal.js` and `css/masterportal.css`).
- Dev server: `npm start` (Vite, HTTPS, self-signed dev cert auto-generated via `prestart`), default `https://localhost:5173`; verified on port 5175.

## Final state
Installation completed and verified. All server processes started for verification were stopped afterwards. No incomplete work.

## Note on source vs. guide
The supplied guide targets end users downloading a prebuilt `examples.zip` from Bitbucket. That artifact was not used; instead the developer/source build path (npm install + build) was used against the already-checked-out repository, which is the appropriate installation method for this workspace.