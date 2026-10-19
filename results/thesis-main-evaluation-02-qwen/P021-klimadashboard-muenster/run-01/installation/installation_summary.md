Installed the Klimadashboard Münster Next.js app in the shared workspace at /workspace (a plain Linux container; no venv — it runs directly on Node).

Steps performed:
1. Prerequisites: Node.js was absent. Installed Node v20.18.1 from the official nodejs.org tarball into /usr/local, and Yarn 1.22.22 via `npm i -g yarn`.
2. Documented install: `cd /workspace && yarn install --network-timeout 600000` → exit 0; 609 packages in node_modules. The project `postinstall` hooks ran and downloaded most data assets into assets/data/.
3. Recovered a partial postinstall failure: `unzip` was missing, so scripts/ms-open-data.sh and scripts/einwohner.sh failed initially. Installed `unzip` (apt-get) and re-ran ms-open-data.sh (succeeded → 25 CSVs). einwohner.sh still failed (credential reason below).
4. Documented start: `yarn dev` → Next.js 15.5.28 "Ready", serving http://localhost:3000 (left running in background, log /tmp/dev-server-final.log).

Objective results (curl): `/` → HTTP 200; `/energie` → HTTP 200; `/mobilitaet` → HTTP 500; `/gebaeude` → HTTP 500; `/klima` → HTTP 500. Dev log shows the 500s are `Module not found: Can't resolve '@/assets/data/einwohner.csv'` and `Can't resolve '@/assets/data/wachstum-recent.csv'` / `bip-recent.csv` (static imports in AutoCardHeader.tsx, WachstumChart.tsx, etc.).

Root cause: those three CSVs are produced by scripts/einwohner.sh, wachstum-recent.sh, bip-recent.sh, all of which POST to https://www.regionalstatistik.de/genesisws/rest/2020/data/tablefile using $REGIONALSTATICT_USER / $REGIONALSTATICT_SECRET. Tested that endpoint directly without credentials → HTTP 401. The credentials are not in .env, .env.example, the process env, or anywhere in the repo, and the installation guide never documents them. The project's own Dockerfile confirms these are normally supplied as Docker build secrets — a required external input not available here.

State: dependencies installed, dev server running at http://localhost:3000, landing page + /energie functional, but 3 of the 4 category pages (mobilitaet, gebaeude, klima) return 500. No source code was modified. Known startup command: `yarn dev` (access http://localhost:3000). To fix the three broken pages, provide REGIONALSTATICT_USER/REGIONALSTATICT_SECRET and re-run the three regional-statistics scripts.