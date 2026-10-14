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

## Installation Summary

**Project:** DCAT Catalog Check (`dcat-catalog-check` v1.1.0)
**Repository/working directory:** `/workspace` (git commit `44583b1`)
**Method used:** Poetry (the guide's recommended method), matching the project's `Dockerfile` and `.gitlab-ci.yml`.

### Steps performed
1. Environment had no Python toolchain. Installed (apt): `python3` (3.10.12), `python3-pip`, `python3-venv`, `python3-dev`, plus build/system libs `gcc`, `libmagic-dev`, `libgdal-dev`, `libgeos-dev`, `libproj-dev`.
2. Installed Poetry via `pip3 install poetry` (Poetry 2.5.1).
3. The project pins `gdal = "3.6.2"` in `pyproject.toml`, which had to compile against system GDAL. Ubuntu 22.04's stock `libgdal-dev` (3.4.1) was too old for the GDAL 3.6.2 Python bindings and failed to build. Added the `ppa:ubuntugis/ppa` repository and installed `libgdal-dev` 3.8.4.
4. Ran `poetry install --no-interaction --no-ansi`. It created virtualenv at `/root/.cache/pypoetry/virtualenvs/dcat-catalog-check-xS3fZVNL-py3.10` and installed all dependencies including the compiled `gdal 3.6.2` package. Exit code 0.
5. Importing `osgeo.gdal` initially segfaulted at interpreter shutdown due to a mismatched PROJ runtime (PPA `libgdal` 3.8.4 linked both `libproj.so.25` and the stale `libproj.so.22`). Fixed by running `apt-get upgrade -y`, which brought `libgeotiff`, `libspatialite`, `libproj-dev` and related libs to the PPA versions. After this, `osgeo.gdal` imports cleanly with exit code 0.

### Final state / access points
- Entry point: `poetry run python dcat_catalog_check.py --url <CATALOG_URL>`
- Helper/optional scripts: `download_catalog.py`, `check_periodicity.py`, `mqa.py`
- Config: `resources/file_types.json`; format checkers in `formats/`
- Dev deps available: `coverage`, `ruff` (`poetry run coverage ...`, `poetry run ruff check .`)

### Verification
- `poetry run python dcat_catalog_check.py --help` → exit 0, full argument list printed.
- `poetry run coverage run -m unittest` → 77 tests, "OK", exit code 0 (80% coverage).
- End-to-end run against a locally served copy of `tests/data/catalog.ttl` produced 45 valid JSON Lines result records with exit code 0.
- Geospatial formats (`geotiff`, `shp`, `gml`) test groups pass, confirming GDAL/geopandas integration works.

No incomplete work remains; the software is installed and functional.

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