## What was done

Working directory: `/workspace` (repo checked out at the pinned SHA), running as root in an Ubuntu 22.04 (x86_64) container.

### Method (per the guide's Setup section)
1. **Prerequisite toolchain**: `mise` was not preinstalled and `brew` does not exist in the container, so mise was installed via the official installer (`curl -fsSL https://mise.run | sh`, non-interactive), landing at `/root/.local/bin/mise` (v2026.10.12).
2. **`mise trust`** → `mise trusted /workspace`.
3. **`mise install`** → all 10 tools pinned in `mise.toml` installed: node 24.18.0 (npm 11.16.0), awscli 2.36.13, fnox 1.31.1, git-cliff 2.13.1, hk 1.53.0, jq 1.8.2, lychee 0.24.2, 1password-cli 2.38.1, glab 1.111.0, trivy 0.72.0.
4. **`mise exec -- npm ci`** → 566 packages installed under the pinned node, exit 0 (npm warns about 24 advisories in the dependency tree; not blocking). The private-ish git dependency `original-rechner` from `gitlab.opencode.de` resolved fine over HTTPS.
5. **Git hooks**: `hk install --global` failed ("requires Git 2.54+ (config-based hooks). Detected git version does not support this") because the container ships git 2.34.1. Followed hk's own suggestion and ran per-repo **`hk install`** (via `mise exec`), which installed `/workspace/.git/hooks/pre-commit` and `/workspace/.git/hooks/commit-msg`. This is per-clone rather than per-machine, as noted in the guide's discussion of the global variant.
6. **App wrapper snapshot** (needed for `mise run start`): `scripts/generate-app-wrapper.sh` requires `wget`, which was missing → installed via `apt-get install -y wget`. Then the snapshot was generated successfully (fetched live `familienportal.de/familienportal/meta/egr` page + sprite into gitignored `/workspace/.app-wrapper/wrapper`).

### Verification (all observed in this session)
- `mise run static-checks` → **exit 0**: prettier format check, `tsc` type-check, oxlint (0 warnings/0 errors on 514 files), stylelint all pass.
- `mise run test-suite` (vitest, `LC_ALL=de-DE.utf8`) → **5147 passed, 1 skipped, 4 failed (246 test files, 242 passing)**. All 4 failures were `Test timed out in 15000ms`/`60000ms`; the set of failing files differed between two full runs (load-dependent flakiness under 8 parallel workers). Every failed file **passes when re-run in isolation** (e.g., the property-based test `refactoring-properties.spec.ts` alone takes 32.7s, exceeding the 15s per-test timeout under full parallel load).
- `MISE_ENV=staging mise run build` → **exit 0**; Vite/Rollup built the widget to `/workspace/dist/` (only benign `import.meta`-in-iife warnings).
- `mise run start` (vite dev server) → "VITE v8.1.5 ready", `http://localhost:5173/` returned **HTTP 200** with the Familienportal host page snapshot: correct title "Elterngeldrechner mit Planer | Familienportal des Bundes", the widget's `id="egr-root"` mount point present, and `/src/application/index.tsx` compiled and served (HTTP 200). Server was stopped afterwards; no leftover processes.

### Resulting state
- Toolchain and environment: mise-managed node 24.18.0/npm 11.16.0 at the repo (active via `mise exec` or `mise activate` in a shell); all other mise tools listed in `mise ls --installed`.
- `/workspace/node_modules` populated (409 top-level entries); `/workspace/dist/` contains a staging build; `/workspace/.app-wrapper/wrapper/` holds the host-page snapshot.
- Git hooks active per-clone (pre-commit, commit-msg).
- Known startup commands: `mise run start` (dev server at http://localhost:5173/), `mise run check` / `mise run test-suite` / `mise run static-checks`, `MISE_ENV=staging|production|preview mise run build`.
- Not attempted (require 1Password "Elterngeld Engineering" vault credentials not available in this environment, and are deployment, not installation, steps): `mise run deploy ...` and any fnox-resolved secrets.

### Incomplete/unknown
- `hk install --global` could not be used due to the container's git version; per-repo hooks are installed instead. No code changes were made to the repository.