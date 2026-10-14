## Installation Summary

**Project:** Föderales Entwicklungsportal (Next.js 16 static developer portal)
**Working directory:** `/workspace` (pre-checked-out repository at the predefined commit SHA)
**Execution context:** Ubuntu 22.04.5 (jammy), x86_64, root shell in the benchmark container.

### Prerequisite setup (not documented as preinstalled)
The environment shipped with no Node.js, npm, or Yarn. I installed them:
- Downloaded the official Node.js 22.20.0 binary tarball from `nodejs.org` and extracted it to `/usr/local` (`node v22.20.0`, `npm 10.9.3`).
- Installed Yarn globally via `npm install --global yarn` → `yarn 1.22.22` (matches the version pinned in the project `Dockerfile`).

### Dependency installation
- Ran `yarn install --frozen-lockfile --network-timeout 600000` in `/workspace`. Completed with `Done in 237.32s` (exit code 0). Only peer-dependency/resolution warnings were emitted; no errors.

### Production build/export (documented method)
- Ran `yarn export` (which maps to `next build --webpack`) in `/workspace`. Completed with exit code 0, `Done in 86.77s`.
- Output written to `/workspace/build` (~21 MB), containing 191 prerendered `index.html` pages plus `_next` static assets, `404.html`, and language routes (`/de`, `/en`).

### Result state
- The built static site is complete and servable. Verification served `/workspace/build` over HTTP and confirmed HTTP 200 for `/`, `/de/`, `/en/`, `/de/resources/`, `/en/resources/joinup/`, `/fit-standards/`.

### Notes
- No `.env.local` was created; the guide lists Plausible analytics variables as optional with defaults, so the build proceeded with defaults.
- The documented dev command (`yarn dev`, port 3000) was not needed for verification since the documented production export path fully succeeded.
- Temporary helper/download files were removed.

### Known startup / access commands
- Dev server: `yarn dev` → http://localhost:3000
- Serve built export: `npx serve@latest build` (or any static HTTP server rooted at `/workspace/build`).

### Abandoned attempts
- Attempted NodeSource `setup_22.x` + `apt install nodejs`; the apt fetch stalled and the command hit the 600s tool timeout, leaving no Node installed. Recovered by using the official Node.js binary tarball instead.