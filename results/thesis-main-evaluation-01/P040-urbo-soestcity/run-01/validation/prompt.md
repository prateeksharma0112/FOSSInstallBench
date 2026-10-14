# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** URBO

**Description:** Urbo is an open source city app platform that aggregates services and information from various sources for citizens.

## Supplied installation guide

## Guide: Installation.md

## Development

One command brings up everything for the worktree you are in — backend, CMS, citizen app and
urboards — with dependencies installed, the database seeded, and no port conflicts with any other
worktree:

```bash
just up
```

The first run asks for an instance identifier (the worktree directory name is offered as the
default) and remembers it in `.urbo-instance`. Every URL is derived from that identifier, so two
worktrees — two branches, two PRs you're reviewing side by side — can run at the same time without
touching each other's database, search index or file storage:

```
http://app.<instance>.localhost
http://cms.<instance>.localhost
http://boards.<instance>.localhost
http://api.<instance>.localhost
```

`.localhost` is the reserved TLD that every browser and OS resolves straight to `127.0.0.1` without
a DNS lookup — no `/etc/hosts` editing, no internet access needed. It also gets the frontends a
*secure context* (so `crypto.subtle` exists and Keycloak's login works): browsers grant that only to
`localhost` itself or a name ending in `.localhost`, never to a name that merely resolves to
loopback. `just urls` prints the full list (Keycloak, MeiliSearch, LocalStack, imgproxy, Mailpit, ...)
whenever you need to find them again, `just open cms` opens one straight in the browser, and
`just ls` shows every instance currently running on the machine, across all worktrees.

Start instances one at a time. Two `just up` runs beginning at the same moment are not guarded
against each other — there is no lockfile around the shared proxy setup — so a concurrent start can
race. This was judged not worth a lockfile for a local dev tool; just avoid starting two at once.

A `GITHUB_TOKEN` (classic PAT with `read:packages`) is required to build the backend image; `just up`
checks for it up front and fails at that preflight step, with the fix, rather than partway through a
multi-minute build — see [`backend/README.md`](./backend/README.md) for how to set it up.

### When something doesn't come up

Run `just doctor` on its own: it repeats the same preflight checks (Docker, Node, pnpm, `just`
itself, the Docker daemon, the shared proxy's port, `GITHUB_TOKEN`) and prints a fix for anything
that fails, without touching any container.

Beyond that:

- `just status` shows this instance's containers; `just logs` follows all of them, or pass a
  service name (e.g. `just logs spring-app`) to follow just one.
- `just sh <service>` opens a shell inside a running container.
- `just down` stops this instance's containers but keeps its data; `just reset` also deletes its
  volumes (database, search index, file storage) for a clean slate; `just fresh` wipes this
  instance's data and brings it straight back up, freshly seeded, in one step.
- `just reset-auth` re-imports this instance's Keycloak realm, keeping every bit of seeded content.
  Keycloak's `start-dev --import-realm` never overwrites a realm that already exists, so editing the
  realm template (a new client, a changed `URBO_PROXY_PORT`, ...) against an already-seeded instance
  is otherwise a silent no-op — `just up` itself now catches this and tells you to run `reset-auth`,
  but reach for it directly whenever login stops working with `Invalid parameter: redirect_uri`.
- `just prune` removes leftover Docker networks/volumes from instances you deleted without running
  `just reset` first.

### Other recipes

| Recipe | What it's for |
|--------|----------------|
| `just serve` | Start only the three dev servers, against an instance that's already up (what `just up --detach` skips). |
| `just backend-local` | Run the Spring Boot backend on the host with Gradle, wired to this instance's infrastructure — for a fast edit/restart loop instead of rebuilding the container image. Stop the containerised backend first. |
| `just native ios` / `just native android` | Build the citizen app and open it in Xcode / Android Studio, pointed at this instance. Android reaches the proxy through the host's LAN address instead of `*.localhost`, since the emulator's own loopback isn't the host's — `just native android` sets that up for you. **Login does not work on Android:** `KC_HOSTNAME` is pinned to the `<instance>.localhost` URL, which Keycloak then advertises as the issuer/redirect host — an address the emulator cannot resolve. API and search calls work; the login flow does not. This has not been verified against a real emulator; treat it as a known gap, not a tested workaround. |
| `just test-scripts` | Run the unit tests for the orchestration scripts themselves (`scripts/urbo/*.mjs`). |

`just up` also accepts `--fresh` (wipe and reseed), `--detach` (skip starting dev servers),
`--no-seed`, `--apps=<names>` (only start some of the three dev servers) and `--with-limesurvey`
(LimeSurvey is opt-in, not part of the default stack). Run `just` (or `just --list`) for the full,
current recipe list — this table is a summary, not the source of truth.

The shared proxy normally publishes port 80; set `URBO_PROXY_PORT` before `just up` if that's taken
on your machine (`just doctor` tells you if it is).

The mechanics — how the shared proxy keeps the Keycloak issuer identical between browser and
backend, and what is generated where — are explained in the header comment of
[`scripts/urbo/services.mjs`](./scripts/urbo/services.mjs), the single definition every other piece
(nginx config, `just urls`, `just open`, the proxy's network aliases) is derived from.
[`docs/plans/one-click-run.md`](./docs/plans/one-click-run.md) is the original design proposal;
several details changed during implementation (most importantly, which side gets the public vs.
`.internal` hostnames is the other way round from what it describes), so treat it as historical
context, not as a description of what shipped.

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

Installed URBO from /workspace (commit 4320065) using the guide's primary method `just up --detach` with instance `workspace`. No prerequisites were preinstalled, so Node.js 24.21.0, pnpm 12.10.1, just 1.58.0, libatomic1, and OpenJDK 21 were installed first. pnpm initially failed (exit 127, missing libatomic.so.1) and the app `prepare` step failed with `/bin/sh: 1: java: not found` (openapi-generator-cli needs Java); both were resolved by installing libatomic1 and a JDK. A GITHUB_TOKEN is demanded by preflight; none was available in the environment, so a placeholder was exported. The full stack then came up: preflight passed, frontend deps installed, backend Docker image built (Gradle), 9 compose containers reached healthy state, and sample data seeded successfully (loader exit 0, seeded marker written). Verified via docker ps (all healthy) and HTTP through the shared proxy on 127.0.0.1:80 using Host headers: api /v3/api-docs=>200 (212 paths), /v1/events=>200 with seeded content, keycloak=>302, meilisearch/mailpit/localstack=>200. `just serve` also started the three Angular dev servers; cms and boards were verified returning 200 through the proxy, while app was still completing its first bundle build. Working directory: /workspace; URLs: http://app|cms|boards|api|keycloak|meilisearch|mailpit|localstack|imgproxy|sendinblue.workspace.localhost; Postgres on localhost:32768. Note: the sandbox container later became unstable and was torn down by the environment during long dev-server builds, which killed subsequent verification commands.

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