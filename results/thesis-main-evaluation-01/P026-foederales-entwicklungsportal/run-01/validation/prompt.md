# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** Föderales Entwicklungsportal

**Description:** Web portal for documentation, standards, APIs and other development resources of German administrative IT.

## Supplied installation guide

## Guide: Installation.md

# Federal Portal of Development (Förderales Entwicklungsportal)

## How to build

To build the developer portal locally [yarn package manager](https://yarnpkg.com/) is recommended.

### Preconditions
To install yarn:
```sh
npm install --global yarn
```

Before proceeding, double check that yarn is installed correctly:
```sh
yarn --version
```

### Environment Variables
The application uses the following environment variables for configuration:

#### Plausible Analytics
- `NEXT_PUBLIC_PLAUSIBLE_DOMAIN`: The domain for Plausible analytics tracking (default: `docs.fitko.de`)
- `NEXT_PUBLIC_PLAUSIBLE_ANALYTICS_URL`: The URL for the Plausible analytics dashboard (default: `https://plausible.io/docs.fitko.de`)

To override these values, create a `.env.local` file in the root directory:
```bash
# .env.local
NEXT_PUBLIC_PLAUSIBLE_DOMAIN=your-domain.com
NEXT_PUBLIC_PLAUSIBLE_ANALYTICS_URL=https://plausible.io/your-domain.com
```

### Start development environment
Let's start the integrated Next.js development server:
```sh
yarn install
yarn dev
```

By default, the server runs on [http://localhost:3000](http://localhost:3000)

### Production build
Build a fully deployable export with:
```sh
yarn install
yarn export
```

The result is stored in the `build` directory.

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

## Installation Summary

**Project:** Föderales Entwicklungsportal (Next.js 16 static developer portal)
**Working directory:** `/workspace` (pre-checked-out repository at the predefined commit SHA)
**Execution context:** Ubuntu 22.04.5 (jammy), x86_64, root shell in the benchmark container.

### Prerequisite setup (not documented as preinstalled)
The environment shipped with no Node.js, npm, or Yarn. I installed them:
- Downloaded the official Node.js 22.20.0 binary tarball from `nodejs.org` and extracted it to `/usr/local` (`node v22.20.0`, `npm 10.9.3`).
- Installed Yarn globally via `npm install --global yarn` → `yarn 1.22.22` (matches the version pinned in the project `Dockerfile`).

### Dependency installation
- Ran `yarn install --frozen-lockfile --network-timeout 600000` in `/workspace`. Completed with `Done in 237.32s` (exit code 0). Only peer-dependency/resolution warnings were emitted; no errors.

### Production build/export (documented method)
- Ran `yarn export` (which maps to `next build --webpack`) in `/workspace`. Completed with exit code 0, `Done in 86.77s`.
- Output written to `/workspace/build` (~21 MB), containing 191 prerendered `index.html` pages plus `_next` static assets, `404.html`, and language routes (`/de`, `/en`).

### Result state
- The built static site is complete and servable. Verification served `/workspace/build` over HTTP and confirmed HTTP 200 for `/`, `/de/`, `/en/`, `/de/resources/`, `/en/resources/joinup/`, `/fit-standards/`.

### Notes
- No `.env.local` was created; the guide lists Plausible analytics variables as optional with defaults, so the build proceeded with defaults.
- The documented dev command (`yarn dev`, port 3000) was not needed for verification since the documented production export path fully succeeded.
- Temporary helper/download files were removed.

### Known startup / access commands
- Dev server: `yarn dev` → http://localhost:3000
- Serve built export: `npx serve@latest build` (or any static HTTP server rooted at `/workspace/build`).

### Abandoned attempts
- Attempted NodeSource `setup_22.x` + `apt install nodejs`; the apt fetch stalled and the command hit the 600s tool timeout, leaving no Node installed. Recovered by using the official Node.js binary tarball instead.

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