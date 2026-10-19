# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** elterngeldrechner

**Description:** Parental allowance calculator and planner for non-binding calculation and planning of parental allowance receipt.

## Supplied installation guide

## Guide: Installation.md

# Elterngeldrechner und Planer

Elterngeldrechner mit Planer im [Familienportal des BMBFSFJ](https://familienportal.de/familienportal/meta/egr).

## Getting Started

Everything you need to get the Elterngeldrechner running locally and out to staging or production.

### Requirements

- **[mise](https://mise.jdx.dev)**: manages the development toolchain, provides the required environment variables, and exposes
  the tasks described below. Install it with `brew install mise`, then activate it in your shell (see the
  [mise docs](https://mise.jdx.dev/getting-started.html)).
- **1 Password CLI + Vault Access**: To trigger deployments from your development machine the integration between the 1password
  app and the cli must be anabled and you must have access to the **Elterngeld Engineering** vault.

### Setup

```sh
mise trust           # one-time, confirms you trust this repo's mise.toml
mise install         # installs the tools pinned in mise.toml
mise exec -- npm ci  # mise exec, so the install runs under the pinned node
hk install --global  # one-time per machine, see "Git hooks" below
```

### Development

```sh
mise run start                        # serve the widget in the host page snapshot
mise run check                        # format, type-check, lint, stylelint and test
mise run static-checks                # everything in check but the suite
mise run test-suite                   # just the vitest suite
mise run audit                        # licences, vulnerabilities and secrets
mise run link-check                   # external links in sources and documentation
```

### Git hooks

[hk](https://hk.jdx.dev) formats and lints the staged files before each commit, and validates the commit subject
against [conventional commits](https://www.conventionalcommits.org). Every step calls the same npm script as
`mise run static-checks`, so the hook cannot drift from the pipeline. See [hk.pkl](hk.pkl) for the current set.

`hk install --global` is per machine rather than per clone, so run it once, from inside this repository. Use
`hk check` to lint on demand, `hk fix` to apply the fixes and `HK=0 git commit …` to bypass the hooks.

### Secrets

Every secret a development task needs, deploying a preview or rolling production back for instance, lives in the
**Elterngeld Engineering** vault in 1Password. [fnox](https://fnox.jdx.dev) resolves it when the task runs, so no
token is written to disk. See [fnox.toml](fnox.toml), which references the secrets without holding their values.

Only secrets specific to the pipeline are CI/CD variables, such as the token for the PostHog release annotation,
scoped to that one job with minimal privileges.

### Deployment

The Elterngeldrechner can be deployed in two ways. Either just the widget, a single javascript file with the
css inlined, together with its documents and images to staging or production, or the full build including the
Familienportal wrapper as a preview in the staging bucket.

On every push to `main` the application is deployed into the staging Familienportal for integration testing. That
portal is only accessible via a virtual private network, so the same push also publishes the `main` preview, which
the team can reach without one. The production deployment happens on every release, see [Release](#release).

If you'd like to make a branch or feature flag variant of the application available for the team, please use the preview
deployment with a specified name. Please remember to delete the deployment again once unused and be aware of the usual
caveats when working on long-living branches.

If you're interested in more details on the deployment process please read
[ADR 0009](architecture-decision-records/0009-deployment-strategy-s3.md), otherwise just use one of the following
commands.

```sh
mise run deploy --preview --name <name>                     # publish a standalone page under preview/<name>/
mise run deploy --preview --name <name> --delete            # empty that preview again
mise run deploy --staging                                   # build and upload to the staging bucket root
mise run deploy --production                                # build and upload to the production bucket root
mise run deploy --production --rollback --ref <tag-or-sha>  # rebuild a past ref and publish it to production
```

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

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

# ENVIRONMENT

You have access to the same container used for installation, including the files and dependencies left by the installation attempt. Each terminal call starts a fresh shell in `/workspace`. Shell-local directory changes, exported variables, and environment activation do not persist between calls. Include any required directory change, environment variables, or activation of an existing environment in each command.

# VALIDATION PROCEDURE

1. Review the guide and installation summary. Use the summary to locate the software and its components, and confirm the installation method, locations, and runtime context through inspection.
2. Identify the expected software behavior described in the guide and select checks appropriate to the resulting installation.
3. Run the checks in the correct directory and runtime environment. If needed, start the installed software within the boundaries below. Prefer evidence of software behavior over file existence alone.
4. Record the commands, observed results, and limitations. Assess the outcome using the definitions below and your own observations.

Distinguish the final installation method from abandoned attempts. Missing files required only by another installation method do not establish failure. A process not already running, or a timed-out or unavailable check, does not by itself establish failure.

# VALIDATION BOUNDARIES

You may inspect files, dependencies, processes and ports, run diagnostic commands, start or run the existing installation, and query local interfaces.

Do not install or update dependencies, build missing artifacts, perform missing setup or migrations, edit files or configuration, or repair the installation. Application startup and normal runtime file creation are permitted only when they do not perform these prohibited actions.

# OUTCOME DEFINITIONS

- `success`: Objective evidence obtained during validation demonstrates that the installation is complete and the software is operational according to the supplied guide.
- `failure`: Objective evidence obtained during validation demonstrates that the resulting installation is incomplete or cannot operate without further installation or repair work.
- `inconclusive`: The evidence is insufficient to establish either success or failure, including when observations are ambiguous or an environmental limitation prevents a reliable assessment.

# FINAL OUTPUT

Return the structured validation report with these three fields:

- `assessed_outcome`: Report `success`, `failure`, or `inconclusive` according to the definitions above.
- `outcome_evidence`: Record observable command results or execution evidence that directly support the assessed outcome. Include the exact command, working directory or runtime context, exit code where available, and relevant output for decisive checks. For an inconclusive assessment, record the observations or execution limitations preventing a decision.
- `assessment_summary`: Explain in detail what you inspected, how you performed validation, and how the observations support your assessment. Include checks that could not be completed, limitations, and unresolved uncertainty.