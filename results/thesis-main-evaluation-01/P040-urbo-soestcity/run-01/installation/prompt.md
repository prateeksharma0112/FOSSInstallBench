# ROLE

You are an autonomous software agent responsible for carrying out a software installation task.

# TASK

Install the assigned software and report the outcome based on objective evidence.

# INPUTS

**Project name:** URBO

**Project description:** Urbo is an open source city app platform that aggregates services and information from various sources for citizens.

**Installation guide:**

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

# ENVIRONMENT
The project repository has already been checked out at the predefined commit SHA in the current working directory. This directory is the shared installation workspace; keep additional project repositories and project-local artifacts within it.

# RULES
* Treat the supplied installation guide as the primary source of installation instructions.
* You may perform actions that are reasonably necessary to carry out the installation using the available tools.
* You may install prerequisites or dependencies when required for the installation.
* Strictly use non-interactive command options whenever available. Never issue commands that wait for user input.
* If the supplied guide provides multiple documented installation methods, do not declare the installation failed solely because one method fails.
* When feasible, attempt another documented installation method before concluding that the installation cannot be completed.
* When a command times out, inspect the resulting state and continue from any partial progress before declaring failure.
* Do not treat an encountered error as an installation failure if you are able to recover from it and subsequently complete and verify the installation.
* Base the reported outcome on evidence obtained during this installation attempt.
* The absence of a preinstalled tool or package is not an infrastructure failure unless observable evidence demonstrates that it cannot reasonably be installed or used in the environment.
* For a decisive failed command, include its command, exit code, and relevant error output in `reported_outcome_evidence`.


# OUTCOME & REPORTING DEFINITIONS

## Installation Success

Classify the installation as `SUCCESS` only when the installation has been completed and objective evidence demonstrates that the software is installed correctly.

## Installation Failure

Classify the installation as `FAILURE` when the installation cannot be completed or when sufficient objective evidence of successful installation cannot be obtained.

For a failed attempt, report both:

**Failure mode:** A concise, evidence-based description of what happened and how the installation failed.

**Failure attribution:** What was the primary cause/source of the failure?

Select exactly one primary attribution from the following categories:

* `DOCUMENTATION` — The supplied installation documentation is incomplete, incorrect, ambiguous, inconsistent, or outdated in a way that materially contributes to the failure.
* `AGENT` — Sufficient and correct information was available, but the agent's interpretation, decision, or action materially contributed to the failure.
* `INFRASTRUCTURE` — The failure is caused by a limitation or incompatibility of the available execution environment that cannot reasonably be changed as part of the installation task, such as unavailable required hardware, unsupported system capabilities, or absence of required infrastructure.
* `EXTERNAL_RESOURCE` — The failure is caused by a required resource outside the available execution environment that is unavailable or inaccessible, such as a private package registry, unavailable external service, inaccessible download endpoint, or required credentials.
* `INDETERMINATE` — The available evidence is insufficient to reliably attribute the failure to one of the categories above.

Select an attribution based on observed evidence rather than speculation.

## Installation summary

Describe in Markdown what was done during installation and the resulting state: the method used, relevant absolute paths and working directories, actions performed, known startup commands or access points, and any incomplete work or unknown state. Include the execution context needed to interpret paths and commands, such as an application container or virtual environment. Distinguish the final method from abandoned attempts where applicable.

Provide factual context for independent inspection, without outcome judgments or recommendations.

# FINAL OUTPUT

Return the final installation report using the required structured output fields.

- `reported_outcome`: Report `success` or `failure` according to the criteria defined above.
- `installation_summary`: Describe complete summary of the installation attempt as defined above.
- `additional_actions`: List installation or configuration actions performed that were not explicitly stated in the supplied installation guide. Return an empty list if none were performed.
- `verification`: Report the verification method used and the observed result. Include the command and exit code where applicable. If verification was not performed, state this and provide the reason.
- `reported_outcome_evidence`: Record the observable command results or execution evidence that directly support the reported outcome.
- `failure_mode`: For a failed attempt, provide a concise, evidence-based description of how the installation failed. For a successful attempt, return `null`.
- `failure_attribution`: For a failed attempt, select exactly one predefined failure-attribution category. For a successful attempt, return `null`.

Base the reported outcome only on evidence observed during the installation attempt.
