## Environment
- Workspace/repo: `/workspace` (checked out at commit 5432007, gitlab ci change)
- OS: Ubuntu 22.04.5 LTS (Linux x86_64). The supplied guide documents macOS, but the same Python/venv install method was used here.
- Virtual environment: `/workspace/.venv` (Python 3.10.12)

## Method used (documented venv/editable install)
1. Installed prerequisites absent from the base image: `python3`, `python3-pip`, `python3-venv` (apt).
2. `cd /workspace && python3 -m venv .venv && source .venv/bin/activate`
3. `pip install --upgrade pip`
4. `pip install -e .` — success. Built editable wheel `pomodoro_timer-0.3.0-0.editable`, installed `PySide6 6.11.2`, `shiboken6`, and the console script `/workspace/.venv/bin/pomodoro`.

## Additional system prerequisites installed (undocumented; needed on Linux)
Qt6 runtime libraries: `libgl1`, `libegl1`, `libglib2.0-0`, `libxkbcommon-x11-0`, `libxcb-cursor0`, `libxcb-xinerama0`, `libdbus-1-3`, `libfontconfig1`, `libsm6`, `libice6`, `libxrender1`, `libxi6`, `libxtst6`, `libxrandr2`, `libxcursor1`, `libxcomposite1`, `libxdamage1`, `libxfixes3`, `libxext6`, `libx11-xcb1`, `libnss3`, `libasound2`. Without these, importing PySide6 failed with `ImportError: libGL.so.1` then `libglib-2.0.so.0`.

## Verification / access
- Console command present: `/workspace/.venv/bin/pomodoro`
- Launch test: `QT_QPA_PLATFORM=offscreen pomodoro` ran until an 8s timeout (exit 124), indicating the Qt window/event loop started without error.
- Test suite: `QT_QPA_PLATFORM=offscreen python -m pytest -q` → 20 passed.

## Startup command
```
source /workspace/.venv/bin/activate
pomodoro
```
(In this headless container a display backend is required, e.g. QT_QPA_PLATFORM=offscreen, or the repo's Docker/noVNC setup.)

## Not attempted / not applicable
- macOS PyInstaller app bundling (`./packaging/build.sh`, `packaging/Pomodoro.spec`, code signing) — macOS-only, N/A on Linux.
- Docker image build — a documented alternative, not needed since the native venv install succeeded.
- MP3 sound files / POMODORO_* env vars were not configured (optional; app degrades gracefully).