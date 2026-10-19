## What was done (container: Ubuntu 22.04, working directory /workspace, repo @seitenbau-dev/formulardesigner v1.0.2 already checked out)

**Prerequisite (not in guide):** Node.js/npm were absent. Installed Node.js v22.20.0 by downloading the official linux-x64 tarball from nodejs.org and extracting it into /usr/local (node v22.20.0, npm 10.9.3 available system-wide). Chose Node 22 LTS because the project uses Vite 8, which requires Node 20.19+/22+.

**Installation (following Installation.md "Beispielanwendung starten" section, `npm run start:example` = `npm run build && cd example && npm install && npm run dev`, executed stepwise):**
1. `npm install` in /workspace — added 287 packages, exit 0 (only peer-dependency warnings for @tiptap, no failures).
2. `npm run build` in /workspace — `tsc -p ./tsconfig.json && vite build && tsc` succeeded, exit 0; produced /workspace/dist/formulardesigner.es.js (~968 kB), /workspace/dist/assets/index.css and .d.ts type declarations.
3. `npm install` in /workspace/example — 128 packages; the example's dependency `@seitenbau-dev/formulardesigner: file:..` resolved as a symlink /workspace/example/node_modules/@seitenbau-dev/formulardesigner -> /workspace (local package linkage).
4. `npm run dev` in /workspace/example — started via `nohup ... &` (non-interactive; log at /tmp/vite-dev.log). Vite v8.3.0 reports "ready in 1071 ms" and is still running in the background, serving at http://localhost:5173/ (Local only, no --host).

**Resulting state / access points:**
- Library source + built dist: /workspace (dist/formulardesigner.es.js, dist/src/**/*.d.ts).
- Example app: /workspace/example; running dev server reachable at http://localhost:5173 (Vite process still active; restart later with `cd /workspace/example && npm run dev`).
- The only entry in the Vite log other than "ready" was a 404 from a deliberately probed non-existent dep-optimizer path during my checks; no app or build errors.

**Incomplete/unknown:** none. A headless browser was additionally installed (/root/.cache/ms-playwright/chromium_headless_shell-1228) solely for verification; temporary files in /tmp were cleaned up (vite log kept at /tmp/vite-dev.log).