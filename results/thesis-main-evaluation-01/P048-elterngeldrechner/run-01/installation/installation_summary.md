## elterngeldrechner installation summary

**Context:** Repository checked out at commit `cbde2eb` in the shared workspace `/workspace` on Ubuntu 22.04 (root). Fresh container — no node, npm, or mise preinstalled.

**Method (final, successful):** Followed the guide's mise-based workflow with adaptations for a headless Linux container.

1. Installed mise to `/root/.local/bin/mise` via the official `https://mise.run` script. Then `mise self-update` from 2025.10.0 → 2026.10.6 (the older version could not resolve the `fnox` backend pinned in `mise.lock`).
2. `cd /workspace && mise trust`.
3. `mise install` — installed all 10 tools in `mise.toml`: node 24.18.0, awscli 2.36.13, fnox 1.31.1, git-cliff 2.13.1, hk 1.53.0, jq 1.8.2, lychee 0.24.2, 1password-cli 2.38.1, glab 1.111.0, trivy 0.72.0. Tools land in `/root/.local/share/mise/installs/` with shims in `/root/.local/share/mise/shims/`.
4. `mise exec -- npm ci` — installed 566 packages into `/workspace/node_modules` under pinned node/npm.
5. Git hooks: `hk install --global` failed on git 2.34.1 (requires git 2.54+ for config-based global hooks), so used per-repo `hk install` → created `/workspace/.git/hooks/pre-commit` and `/workspace/.git/hooks/commit-msg`.
6. `mise run generate-app-wrapper` (needs `wget`) fetched the Familienportal host-page snapshot into `/workspace/.app-wrapper/wrapper`.

**Resulting state / access points:**
- Dev server: `mise run start` → vite serves the widget at `http://localhost:5173/` (verified HTTP 200).
- Build: `MISE_ENV=staging mise run build` → artifacts in `/workspace/dist/`.
- Static checks pass: `mise run type-check`, `lint`, `format`, `stylelint` (all exit 0).
- Test suite: `mise run test-suite` → 5,152 tests, 5,144 pass, 1 skip, 7 fail; all 7 failures are `Test timed out` under full-suite contention, and the failing files pass in isolation.

**Incomplete/unknown:** Deployment, secret-resolution (`fnox`), license/vulnerability/secret audits, and link-check tasks require 1Password vault access and/or VPN and were not exercised. One non-fatal vfox plugin metadata warning persists for the 1password-cli plugin, though `op --version` reports 2.38.1.