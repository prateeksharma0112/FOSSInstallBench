**Environment:** Shared installation workspace container (Ubuntu 22.04.5, root); project repo at `/workspace`. No Node.js/npm/yarn were preinstalled.

**Steps performed:**
1. Installed Node.js v22.17.0 (official linux-x64 binary tarball from nodejs.org) into `/opt/nodejs`, with symlinks for `node`, `npm`, `npx` in `/usr/local/bin`.
2. Installed Yarn globally per the guide: `npm install --global yarn`; the binary landed in `/opt/nodejs/bin/yarn`, so a symlink was added at `/usr/local/bin/yarn`. Verified: `yarn --version` → 1.22.22.
3. Ran `yarn install --frozen-lockfile` in `/workspace`. The first attempt against the default `registry.yarnpkg.com` failed with repeated `ESOCKETTIMEDOUT` errors; resolved by setting the yarn registry to `https://registry.npmjs.org` (same packages, different mirror). Install then completed in ~197 s ("Done in 197.07s.", exit code 0).
4. Ran the production build per the guide: `yarn export` (Next.js 16.3.4, `next build --webpack` with `output: 'export'`). Build succeeded in ~116 s (exit code 0), prerendering ~150 static pages (DE/EN resources, fit-standards, search pages, etc.).

**Resulting state:**
- `/workspace/node_modules` — installed dependencies.
- `/workspace/build` — fully deployable static export (index.html, de/, en/, fit-standards/, resources/, _next assets, robots.txt, search-data), as documented in the guide.
- No `.env.local` was created; the Plausible analytics variables have defaults documented in the guide, so none were required.

**Known access points (from the guide):**
- Development: `yarn dev` → http://localhost:3000 (not started as part of final state).
- Served production export: `yarn start` (`npx serve@latest build`) → http://localhost:3000.

**Verification performed:** Started the static server against `/workspace/build` on port 3000; `curl` returned HTTP 200 for `/`, `/de/`, `/fit-standards/`, `/resources/meta/`, and the page title rendered as "Föderales Entwicklungsportal - Entwicklerressourcen für die digitale Verwaltung". The temporary test server was stopped afterward.

**Abandoned/failed attempts:** The initial `yarn install` against `registry.yarnpkg.com` failed (network timeout from this environment); recovered by switching to `registry.npmjs.org` as described above.