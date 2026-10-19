**Environment:** Ubuntu 22.04 (jammy) container, x86_64, root user; project at /workspace (DCAT Catalog Check v1.1.0, python ^3.10). Initially no Python and no Poetry were present.

**Method used (final):** the documented Poetry method from Installation.md.

**Actions performed:**
1. Installed system prerequisites via apt-get: python3 (3.10.6, matching the Dockerfile's python:3.10 base), python3-venv, python3-dev, python3-pip, gcc, g++, make, libgdal-dev, libgeos-dev, libproj-dev, libmagic-dev (per the project's Dockerfile dependency list).
2. Installed Poetry 2.5.1 via pip (`python3 -m pip install poetry`).
3. First `python3 -m poetry install` run failed during the PEP 517 build of the pinned `gdal==3.6.2` sdist against Ubuntu 22.04's system GDAL 3.4.1 headers (`ogr_recordbatch.h: No such file or directory`, `GDT_UInt64 undeclared`, etc.).
4. Built and installed GDAL 3.6.2 from source (git clone OSGeo/gdal v3.6.2 → cmake → make -j8 → install to /usr/local, `ldconfig`); `gdal-config --version` = 3.6.2dev, `gdal-config --cflags` = `-I/usr/local/include`.
5. Re-ran `python3 -m poetry install --no-interaction --no-ansi` in /workspace — completed with exit 0 ("Installing the current project: dcat-catalog-check (1.1.0)"); a follow-up run reports "No dependencies to install or update" (idempotent).

**Resulting state:**
- Poetry virtualenv: /root/.cache/pypoetry/virtualenvs/dcat-catalog-check-xS3fZVNL-py3.10 (Python 3.10.12, valid), with all 62 locked dependencies including gdal 3.6.2, fiona 1.10.1, geopandas 1.1.1, frictionless 5.18.1, rdflib 7.1.4, requests 2.32.4, python-magic, pypdf, pillow, pyarrow 18.1.0.
- Startup/access point: `cd /workspace && python3 -m poetry run python dcat_catalog_check.py --url <DCAT_CATALOG_URL> > results.jsonl` (equivalent: `poetry shell` then `python dcat_catalog_check.py ...`, per the guide).

**Verification (all observed):**
- `python3 -m poetry run python -c "..."` importing magic, requests, rdflib, frictionless, geopandas, fiona, pypdf, PIL, pyarrow, geojson, osgeo.gdal → all import; gdal 3.6.2 (exit 0).
- `python3 -m poetry run python dcat_catalog_check.py --help` → exit 0, all documented parameters present (--url, --log_file, --results, --verbose, --debug, --recheck, --no-recheck, --check-format, --force-check-format, --check-http-5xx).
- `python3 -m poetry run coverage run -m unittest --buffer` (README-documented test command) → "Ran 77 tests in 2.018s / OK".
- End-to-end: served bundled tests/data via local HTTP on port 8000, ran the documented basic run `python3 -m poetry run python dcat_catalog_check.py --url http://localhost:8000/catalog.ttl > results.jsonl` → exit 0, 45 valid JSON Lines results (22 good / 23 bad checks, matching the sample catalog's good/bad distributions; 16 formats including GDAL/geopandas-dependent SHP and GEOTIFF).
- Documented recheck run `... --results results.jsonl --recheck` → exit 0, 27 valid results.
- Cleanup: local test HTTP servers killed; test-suite artifact /workspace/my_api_key (0-byte log file created by tests) removed; `git status --short` clean.

**Incomplete/unknown:** none. (Docker build method from the guide was not used; the native Poetry path succeeded.)