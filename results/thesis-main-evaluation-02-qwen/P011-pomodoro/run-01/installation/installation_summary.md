**Environment:** Shared installation workspace at `/workspace` (Ubuntu 22.04.5 LTS container, root user; the guide targets macOS, but the package supports Linux per `src/pomodoro/persistence/paths.py`). The project repo was pre-checked-out at `/workspace`.

**Method used (guide's primary method):**
1. Installed prerequisites via apt (none preinstalled): `python3` (3.10.6, meeting the guide's 3.10+ requirement), `python3-venv`, `python3-pip`, plus the Qt/X11 runtime libraries the project's own Dockerfile uses for the `xcb` Qt platform plugin (`libxcb-xkb1`, `libxkbcommon0`, `libgl1`, `libegl1`, `libfontconfig1`, `libfreetype6`, etc.) and `xvfb` (a virtual display, to launch the GUI headlessly for verification).
2. In `/workspace`: `python3 -m venv .venv`, then `pip install -e .` → installed `pomodoro-timer 0.3.0` (editable) and its dependency `PySide6 6.12.0`.

**Resulting state:**
- Virtual environment: `/workspace/.venv`
- Console command: `/workspace/.venv/bin/pomodoro` (entry point `pomodoro.cli:main` from `pyproject.toml`)
- Runtime data directory (Linux/XDG): `/root/.local/share/Pomodoro/` containing `pomodoro.db` (auto-created on launch)

**Known startup command:** `cd /workspace && source .venv/bin/activate && pomodoro` (opens the Qt GUI window; on a headless machine a display such as Xvfb is required, e.g. `DISPLAY=:99 pomodoro`).

**Verification performed:**
- `.venv/bin/python -c "import pomodoro, pomodoro.cli, pomodoro.gui.app"` → OK; `pip show pomodoro-timer` → 0.3.0.
- Started `Xvfb :99`, ran `DISPLAY=:99 QT_QPA_PLATFORM=xcb ./.venv/bin/pomodoro`; the process stayed running and `xwininfo -root -tree` showed a live 960x640 "Pomodoro" window on the display (repeated in a second clean run).
- `pytest tests/ -q` in the venv → 20 passed.
- Background verification processes (Xvfb, app) were killed afterwards; no leftover processes.

**Documented methods not used (unnecessary):** `packaging/build.sh` (PyInstaller `Pomodoro.app`, macOS-only) and the Docker/noVNC method (`docker build`/`docker run`); the primary venv installation succeeded and was fully verified.