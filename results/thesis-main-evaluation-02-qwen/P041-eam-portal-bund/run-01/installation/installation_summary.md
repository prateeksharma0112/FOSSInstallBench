## Installation Summary

**Project:** EAM-Portal Bund (Next.js 15.3.0 / React 19 static-export portal)
**Working directory:** `/workspace` (shared installation workspace, Ubuntu 22.04.5 container, x86_64, running as root)

### Prerequisite installation (not preinstalled)
- Node.js and npm were absent from the container (`node: command not found`).
- Downloaded official Node.js **v22.23.3** tarball from `nodejs.org` (satisfies the guide's "Voraussetzung: Node.js 22"), extracted to `/opt/node22`, and symlinked `node`, `npm`, `npx` into `/usr/local/bin`.
- Verified: `node --version` → `v22.23.3`, `npm --version` → `10.9.9`.

### Guide steps (all executed from `/workspace`)
1. **`npm ci`** — exit code 0. 382 packages installed into `/workspace/node_modules` (npm audit reported 29 pre-existing vulnerabilities; not blocking).
2. **`npm run lint`** (`next lint`) — exit code 0: "✔ No ESLint warnings or errors".
3. **`npm run build`** (`next build`) — exit code 0. Compiled successfully, type-checked, and produced the static export in **`/workspace/out/`** (10 static pages: `/`, `/ea-repository`, `/eam-unterstuetzung`, `/prinzipien-richtlinien`, `/referenzarchitekturen`, `/technologie-radar`, `/_not-found`, plus `404.html` and `_next` assets).
4. **`npm run dev`** — launched in background; Next.js 15.3.0 dev server ready on `http://localhost:3000`. `curl http://localhost:3000/` returned **HTTP 200** and `<title>EAM Portal Bund - Enterprise Architecture Management</title>`. The dev server was then stopped and confirmed down (port 3000 no longer responding).

### Resulting state
- Installed software: `/opt/node22` (Node 22.23.3 runtime) + `/workspace/node_modules` (project dependencies).
- Build artifact: `/workspace/out/` (static export, deployable as-is, e.g. to a web root / GitLab Pages).
- Known startup commands from the guide: `npm run dev` (http://localhost:3000), `npm run build` (static export to `out/`), `npm run lint`.
- No incomplete work; all documented steps succeeded.