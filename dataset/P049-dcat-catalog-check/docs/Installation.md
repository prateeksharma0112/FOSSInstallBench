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

