## Summary

**Method:** Followed the supplied `Installation.md`/README (`yarn install`, then `yarn dev`).

**Context:** Ubuntu 22.04 container; repository checked out at `/workspace` (commit `ffb429f`). No Node.js/npm/yarn were present initially.

**Steps taken:**
1. Installed Node.js **v20.18.0** from the official nodejs.org Linux-x64 tarball into `/usr/local` (Node 20 matches the project's `Dockerfile` base image `node:20-alpine`). Verified `node -v` = v20.18.0, `npm -v` = 10.8.2.
2. Installed **Yarn 1.22.22** globally (`npm install -g yarn@1.22.22`), since the guide uses `yarn`.
3. Installed the OS prerequisite **unzip** via `apt-get` (required by the repo's data-download scripts in `scripts/`).
4. Ran **`yarn install`** from `/workspace` (exit code 0, ~302s). It installed 609 packages (~810 MB) into `/workspace/node_modules` and executed the `postinstall` hook (`scripts/postinstall.sh`), which downloaded data files into `/workspace/assets/data/` and ran `husky install` (git hooks installed).

**Resulting state:**
- Dependencies installed at `/workspace/node_modules`.
- Startup command: `yarn dev` (→ `next dev`), serving at `http://localhost:3000`. Also available: `yarn build` / `yarn start`.
- `.env` contains `NEXT_PUBLIC_DIRECTUS_URL=https://cms.klimadashboard.ms`.

**Final method vs. abandoned attempts:** Only one installation method was documented and used; no alternative methods were attempted/abandoned.

**Incomplete/unknown state:** The `postinstall` data-download scripts `scripts/bip-recent.sh`, `scripts/wachstum-recent.sh`, and `scripts/einwohner.sh` call the Regionalstatistik Genesis REST API and require `REGIONALSTATISTIK_USER` / `REGIONALSTATISTIK_SECRET` credentials (the project's Dockerfile injects these as build secrets). Without them the endpoints return non-ZIP error payloads, so `assets/data/wachstum-recent.csv`, `assets/data/bip-recent.csv`, and `assets/data/einwohner.csv` remain absent. As a result the data pages `/klima`, `/energie`, `/mobilitaet` return HTTP 500 (missing CSV imports in `components/Tiles/Climate/Wachstum/WachstumChart.tsx`), while the root `/` route returns HTTP 200. This reflects missing external data credentials, not a dependency-installation failure. All other data scripts succeeded (trafficload, stadtradeln, ms-open-data, ms-climate-data, ms-buildings-data, ms-cars).