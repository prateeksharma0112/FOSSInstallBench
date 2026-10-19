# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** DCAT Catalog Check

**Description:** Checking links and formats in a DCAT catalog.

## Supplied installation guide

## Guide: Installation.md

# DCAT Catalog Check

This project is a Python script designed to monitor and validate links in a DCAT catalog.

The script is particularly useful for maintaining the integrity of distributions by ensuring that links are active and files are correctly formatted, thus helping to avoid issues related to broken links and invalid file types.


## Installation

Follow the steps below to set up the **DCAT Catalog Check** on your local machine.

### Installation with Poetry

Using **Poetry** is recommended for dependency management and virtual environment handling.

1. **Install Dependencies**

   Navigate to the project directory and install the project’s dependencies (including development dependencies) using Poetry:

   ```sh
   poetry install
   ```

   This command will create a virtual environment and install all necessary packages as specified in the [`pyproject.toml`](./pyproject.toml) file.

2. **Activating the Virtual Environment**

   Poetry automatically manages virtual environments. You can activate the virtual environment with:

   ```sh
   poetry shell
   ```

   To exit the virtual environment, simply run:

   ```sh
   exit
   ```

## Usage

### Parameters

The **DCAT Catalog Check** script accepts several command-line arguments to customize its behavior. Below is a detailed explanation of each parameter:

| Parameter | Description | Type | Default |
| --------- | ----------- | ---- | ------- |
| `--url` | The URL of the DCAT catalog to check. | String | Required |
| `--log_file` | Path to the log file for storing detailed output. | String | None |
| `--results` | File path to load results from previous runs. | String | None |
| `--verbose` | Enable verbose logging for more detailed output. | Flag | Off |
| `--debug` | Enable debug logging for troubleshooting purposes. | Flag | Off |
| `--recheck` | Use the previous results (specified by `--results`) as input for rechecking only. | Flag | Off |
| `--no-recheck` | Only check new entries from the catalog without rechecking existing results. | Flag | Off |
| `--check-format` | Specify a single format to check (e.g., `JSON`, `JPEG`). | String | None |
| `--force-check-format` | Force checking distributions with the specified format, regardless of previous results. | String | None |
| `--check-http-5xx` | Recheck entries that encountered HTTP 5xx errors in previous runs. | Flag | Off |

### Example Usage

**Basic Run:**

To check a DCAT catalog and save the results:

```sh
poetry run python dcat_catalog_check.py --url https://example.com/catalog.xml > results.jsonl
```

The catalog (including possible subsequent pages) is completely downloaded and checked. The result is written to the file `results.jsonl` in *JSON Lines text file format*.

**Recheck Previous Results:**

To recheck only existing results from a previous run:

```sh
poetry run python dcat_catalog_check.py --url https://example.com/catalog.xml --results results.jsonl --recheck
```

**Check New Entries Only:**

To check only new entries without rechecking the existing ones:

```sh
poetry run python dcat_catalog_check.py --url https://example.com/catalog.xml --results results.jsonl --no-recheck > new.jsonl
mv new.json results.jsonl
```

The results from a previous run from the file `result.jsonl` are used. The catalog is processed completely. Only new data records are checked. All results (new ones as well as the old ones that have not been checked again) are output to the file `new.jsonl`. Once the check is complete, the old results file is overwritten with the new one.

**Debugging and Verbose Output:**

To enable verbose and debug logging:

```sh
poetry run python dcat_catalog_check.py --url https://example.com/catalog.xml --verbose --debug
```

**Format-Specific Checks:**

To check only a specific format (e.g., `JSON`):

```sh
poetry run python dcat_catalog_check.py --url https://example.com/catalog.xml --check-format JSON
```

**Force Format Check:**

To force-check a specific format regardless of previous results:

```sh
poetry run python dcat_catalog_check.py --url https://example.com/catalog.xml --force-check-format JSON
```

## Configuration

### File Formats

The script reads the allowed file formats from [`resources/file_types.json`](./resources/file_types.json)
file. This file defines the MIME types that are considered valid for each
format and should be placed in the same directory as the script.

#### Example `file_types.json`

```json
{
  "HTML": [
    "text/html"
  ],
  "JPEG": [
    "image/jpeg"
  ],
  "JSON": [
    "application/json", "text/plain"
  ]
}
```

## Docker

You can run the script in a Docker container. See the [Dockerfile](./Dockerfile) for more information.

### Build and Run

1. Build the Docker image:

    ```sh
    docker build -t dcat-catalog-check .
    ```

2. Run the Docker container:

    ```sh
    docker run --rm dcat-catalog-check --url https://example.com
    ```

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

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