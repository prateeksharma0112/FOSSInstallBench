## Method
Followed the supplied Installation.md (git clone → cd → `bun install` → `bun dev`, plus the Konfiguration section for `.env.local`). The repository was already checked out at the predefined SHA in /workspace, so the clone step was unnecessary. All work was performed as root inside the shared installation container (Ubuntu 22.04, x86_64).

## Prerequisites installed (not in guide, required)
- **Node.js v22.23.3** (official nodejs.org linux-x64 tarball, extracted into /usr/local → /usr/local/bin/node, npm 10.9.9). Satisfies the guide's "Node.js 18 oder höher" requirement.
- **Bun 1.4.3** (official oven-sh/bun GitHub release, linux-x64 binary installed to /usr/local/bin/bun). The guide lists Bun as recommended or npm/yarn as alternatives; Bun was chosen.
- **unzip 6.00** via apt-get (needed to extract the Bun zip).

## Installation steps (per guide)
1. `cd /workspace && bun install` — exit 0, 511 packages installed in ~160s. Bun blocked 2 postinstall scripts; ran `bun pm trust @tailwindcss/oxide unrs-resolver` (both official npm packages providing native binaries for Tailwind 4 and the linter resolver), then re-ran `bun install` — both postinstalls executed successfully, exit 0.
2. Configuration: `cp .env.example .env.local` in /workspace, then replaced the DASHBOARD_PASSWORD placeholder with a dev value. MONGODB_URI/MONGODB_DB left as the template placeholders — the guide documents MongoDB as optional.
3. `bun dev` (Next.js 15.4.10 + Turbopack) started in background via nohup, log at /tmp/devserver.log. Server reports: `✓ Ready in 2.3s`, Local: http://localhost:5173.

## Resulting state
- Working directory: /workspace (repo root); node_modules present; .env.local created.
- Dev server running (background, log /tmp/devserver.log) at http://localhost:5173; restart with `bun dev` from /workspace.
- Verified pages: `/` (HTTP 200, title "KI Führerschein Regensburg"), `/certificate` (200), `/dashboard` (200), `/settings` (200), `/imprint` (200), `/journey/1` (200).

## Known issues (application-level, not installation)
- `/metrics` → 500: placeholder `MONGODB_URI` in .env.local is not a resolvable cluster (`querySrv EBADNAME`); guide explicitly states the app works without MongoDB.
- `/chapter/[id]` → 500: `ReferenceError: localStorage is not defined` during SSR of a `'use client'` page (upstream code defect in /workspace/src/app/chapter/[chapterId]/page.tsx), unrelated to installation.
- No work left incomplete; server was left running.