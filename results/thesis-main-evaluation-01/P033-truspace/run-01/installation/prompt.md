# ROLE

You are an autonomous software agent responsible for carrying out a software installation task.

# TASK

Install the assigned software and report the outcome based on objective evidence.

# INPUTS

**Project name:** TruSpace

**Project description:** Self-hosted, decentralized document collaboration platform that synchronizes documents between organizations over IPFS and supports local AI-assisted document analysis.

**Installation guide:**

## Guide: Installation.md

# Local Setup

Run TruSpace on your own machine and access it at `http://localhost:3000`.

## Installation

```bash
git clone https://github.com/openkfw/TruSpace.git
cd TruSpace
./start.sh
```

On the **first run**, `./start.sh` detects that no `.env` file exists and launches the configuration wizard. Select profile **`1) local-dev`** and confirm the defaults with ENTER. TruSpace will then start automatically.

Once running, open [http://localhost:3000](http://localhost:3000) in your browser.

!!! tip "Re-run the wizard at any time"
`bash
    ./start.sh --configure-env
    `

## Options

| Flag               | Effect                                                       |
| ------------------ | ------------------------------------------------------------ |
| `--no-ai`          | Disable Ollama / Open WebUI to save RAM                      |
| `--dev`            | Build images locally instead of pulling                      |
| `--local-frontend` | Run the Next.js frontend outside Docker (enables hot reload) |

### Development with hot reload

If you are actively working on the frontend or backend, you can run those outside Docker while keeping the infrastructure (IPFS, database) containerised:

=== "Frontend hot reload"

    ```bash
    # Terminal 1 — infrastructure + backend in Docker
    ./start.sh --local-frontend

    # Terminal 2 — frontend with hot reload
    cd frontend
    npm install
    npm run dev
    ```

=== "Frontend + backend hot reload"

    ```bash
    # Terminal 1 — IPFS and AI only
    docker compose up ipfs0 cluster0 ollama webui -d

    # Terminal 2 — backend
    cd backend && npm install && npm run dev

    # Terminal 3 — frontend
    cd frontend && npm install && npm run dev
    ```

## Managing Containers

```bash
# View running containers
docker ps

# Follow logs
docker compose logs -f

# Stop (keeps data)
docker compose down

# Stop and delete all data ⚠️
docker compose down -v
```

## Data & Backups

All persistent data is stored in `./volumes/` inside the project folder.

```bash
# Back up
docker compose down
tar czf truspace-backup-$(date +%Y%m%d).tar.gz ./volumes .env
docker compose up -d

# Restore
docker compose down
rm -rf ./volumes
tar xzf truspace-backup-<date>.tar.gz
docker compose up -d
```

## Troubleshooting

**Port already in use**

```bash
lsof -i :3000   # find what's using the port
kill -9 <PID>
```

**Volume permission errors**

```bash
sudo chown -R 1000:1000 ./volumes
```

**Database error after an update**

```bash
# ⚠️ Deletes all accounts and workspace metadata; IPFS documents are unaffected
rm ./volumes/db/truspace.db
docker compose restart backend
```

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
