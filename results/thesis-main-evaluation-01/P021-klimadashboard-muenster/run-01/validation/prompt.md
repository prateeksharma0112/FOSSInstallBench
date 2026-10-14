# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** Klimadashboard Münster

**Description:** The Münster Climate Dashboard visualizes real-time information about the city of Münster's climate footprint. The dashboard displays data with various graphs in a tile-based layout, with separate pages for each of the four categories. The data comes from many different providers, including the City of Münster's open data portal, the German Meteorological Service (DWD), and BrightSky.

## Supplied installation guide

## Guide: Installation.md

## Getting Started

To run the Klimadashboard application on your local machine, first clone the repository:

> git clone https://github.com/your-username/klimadashboard.git
> cd klimadashboard

Then, install the dependencies:

> yarn install

Finally, start the development server:

> yarn dev

You should now be able to access the application at `http://localhost:3000`.

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

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