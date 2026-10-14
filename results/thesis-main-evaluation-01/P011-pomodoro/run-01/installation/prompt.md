# ROLE

You are an autonomous software agent responsible for carrying out a software installation task.

# TASK

Install the assigned software and report the outcome based on objective evidence.

# INPUTS

**Project name:** Pomodoro

**Project description:** Local focus timer for greater efficiency in everyday administrative work: fixed work blocks, conscious breaks and honest time tracking that also counts interrupted focus sessions.

**Installation guide:**

## Guide: Installation.md

## Installation

Requires Python 3.10+ on macOS.

```bash
git clone <this repo>
cd pomodoro
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

This installs the `pomodoro` console command (via the entry point defined
in `pyproject.toml`) into your active environment.

## Starting it

```bash
pomodoro
```

This opens the app window. Configure Focus/Break minutes, round count,
and the optional long break in the "Einstellungen" panel, then hit
**Start**. Switch to the **Statistik** tab any time to see your history.

## Building a double-clickable macOS app

If you'd rather launch Pomodoro from the Dock / Launchpad than from a
terminal, bundle it into a standalone `Pomodoro.app` with
[PyInstaller](https://pyinstaller.org/):

```bash
./packaging/build.sh
```

That script installs the build dependency (`pip install -e ".[package]"`),
renders the app icon, runs PyInstaller against
[`packaging/Pomodoro.spec`](packaging/Pomodoro.spec), and ad-hoc code-signs
the result (required to run on Apple Silicon). When it finishes:

```bash
cp -R dist/Pomodoro.app /Applications/
open /Applications/Pomodoro.app
```

The bundle is self-contained — it ships its own Python and Qt, so it runs
on any Mac (macOS 11+) without a Python install. Pass `--dmg` to also get
a `dist/Pomodoro.dmg` for copying it to another machine:

```bash
./packaging/build.sh --dmg
```

Because the app isn't signed with an Apple Developer ID, the first launch
on another Mac needs a right-click → **Open** (or *System Settings →
Privacy & Security → Open Anyway*) to get past Gatekeeper. On the machine
that built it, it just opens.

The phase-end sounds and all settings/history work exactly as in the
terminal version — see the two sections below.

## Adding your own sounds

The app plays an MP3 at the end of each Focus round and each Break. Drop
your own files into [`sounds/`](sounds/) using these exact names:

| File             | Played when...                 |
|-------------------|--------------------------------|
| `focus_end.mp3`  | a Focus round finishes          |
| `break_end.mp3`  | a short or long Break finishes  |

No MP3s are shipped in this repo (see [`sounds/README.md`](sounds/README.md)).
Without them the app doesn't crash — it just falls back to a terminal
beep and shows a small hint in the window. The lookup folder can be
overridden with the `POMODORO_SOUNDS_DIR` environment variable.

**In the packaged `Pomodoro.app`**, whatever `sounds/` files were present
at build time are bundled inside the app. To swap them afterwards without
rebuilding, drop `focus_end.mp3` / `break_end.mp3` into
`~/Library/Application Support/Pomodoro/sounds/` — that location is
checked first and wins over the bundled copies.

## Running Pomodoro in a container

The primary way to use Pomodoro is still the native macOS app above, but a
[`Dockerfile`](Dockerfile) is also provided to make it cloud-ready — the same
window, unmodified, made reachable from a plain browser tab:

```bash
docker build -t pomodoro .
docker run --rm -p 6080:6080 \
  -v pomodoro-data:/home/pomodoro/.local/share/Pomodoro \
  pomodoro
```

Then open <http://localhost:6080/vnc.html> — the actual Qt window is
rendered on a virtual display inside the container and streamed to the
browser via VNC/noVNC (see [`docker/entrypoint.sh`](docker/entrypoint.sh)).
There is no separate "web version"; it's the same app.

Two things behave differently than on macOS, both by design of what a
container is:

- **Sound and system notifications are silent.** `afplay`/`osascript` don't
  exist on Linux, and this image doesn't bridge PulseAudio/D-Bus out to the
  host — the app already degrades gracefully in that case (a terminal beep
  instead of the sound file, no notification), so nothing crashes, but you
  won't hear or see either.
- **Data only survives a restart if you mount a volume**, as in the command
  above — otherwise settings and history disappear with the container. The
  data directory can also be overridden explicitly with `POMODORO_DATA_DIR`.

## Configuration & data storage

Settings (last-used timer configuration, theme, project tag) and your
focus history are stored automatically under a per-OS user data directory
(`src/pomodoro/persistence/paths.py`) — `~/Library/Application Support/Pomodoro/`
on macOS, `~/.local/share/Pomodoro/` on Linux (including the container image,
respecting `$XDG_DATA_HOME` if set), or `%APPDATA%\Pomodoro\` on Windows.
Set `POMODORO_DATA_DIR` to use an explicit location instead:

```
settings.json   # last-used configuration (JSON)
pomodoro.db     # completed focus rounds (SQLite)
```

Every Focus round is appended to `pomodoro.db` with its timestamp,
duration, optional project tag, and whether it ran to completion —
that's the data the Statistics tab aggregates into "today / this week /
all-time" totals and the 7-day chart. Since 0.2.0, a Focus round you
cancel early is recorded too, with the time actually elapsed up to that
point, instead of being discarded; only Break phases are never recorded
at all. You can wipe this history from inside the app (Statistik tab →
"Historie zurücksetzen"), which asks for confirmation first since it
can't be undone.

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
