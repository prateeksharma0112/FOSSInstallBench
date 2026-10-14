**Environment:** Ubuntu 22.04.5 LTS container, `/workspace` (git commit 7acedda). Node.js/npm were not preinstalled.

**Steps performed:**
1. Installed Node.js 24 via NodeSource: `curl -fsSL https://deb.nodesource.com/setup_24.x -o /tmp/nodesource_setup.sh`, `bash /tmp/nodesource_setup.sh`, `apt-get install -y nodejs`. Result: node v24.21.0, npm 11.19.0. (Chosen to match the repo's `.gitlab-ci.yml` image `node:24-alpine`; the project has no `engines` field.)
2. Root library install: `cd /workspace && npm install` → "added 287 packages" (peer warnings for tiptap, 26 audit vulns reported; non-blocking).
3. Library build: `cd /workspace && npm run build` (script: `tsc -p ./tsconfig.json && vite build && tsc -p ./tsconfig.json`) → exit 0, generated `dist/formulardesigner.es.js` (965 kB), `dist/assets/index.css`, and `dist/src/index.d.ts` + `dist/src/types/index.d.ts`.
4. Example app install: `cd /workspace/example && npm install` → "added 128 packages", 0 vulnerabilities. The example depends on the library via `"@seitenbau-dev/formulardesigner": "file:.."`.
5. Example app run: `cd /workspace/example && npm run dev` (vite) → server ready at `http://localhost:5173` in ~321 ms.
6. Example app build: `npx tsc -b && npx vite build` → exit 0.

**Final state / access:**
- Library source build artifacts at `/workspace/dist/`.
- Example app installable/startable from `/workspace/example` — the documented `npm run start:example` script (root) does `npm run build && cd example && npm install && npm run dev`; all its component commands were executed and succeeded.
- Example app served at `http://localhost:5173` (HTTP 200); dev server was stopped after verification.

**Method notes:** The guide documents both consuming via the published npm package (`npm install @seitenbau-dev/formulardesigner`) and running the bundled example. Network access to npmjs.org was available; the local `file:..` linked build path was used to verify the actual repository. A direct Node.js ESM `import` of the built package fails only on the imported `.css` file (expected for a browser/Vite component library); bundler-based consumption via the example app works.