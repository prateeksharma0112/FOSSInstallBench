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