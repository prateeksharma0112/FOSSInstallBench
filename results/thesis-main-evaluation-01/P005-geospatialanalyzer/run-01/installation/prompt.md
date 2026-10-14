# ROLE

You are an autonomous software agent responsible for carrying out a software installation task.

# TASK

Install the assigned software and report the outcome based on objective evidence.

# INPUTS

**Project name:** GeospatialAnalyzer

**Project description:** Open source software for providing a web service that enables the automated collection and analysis of geodata – e.g., as a basis for integration into digital application and administrative procedures.

**Installation guide:**

## Guide: Installation.md

# Installation and Debugging

## Prerequisites

You need `Node.js` v24 or higher (although older version might work) installed on your machine.
For example, you can run the following [guide](https://learn.microsoft.com/de-de/windows/dev-environment/javascript/nodejs-on-windows) for windows.
You also need `pnpm` as package manager. Check out the [installation guide](https://pnpm.io/installation).
You need a database connection, as described in the [section _Database_](#database).
If you want to use docker to run this project, you need an installed and _running_ docker service. More Information can be found in [section _Docker_](#docker).

## Configuration

The project uses the `.env` or the `.env.dev` file for configuring your instance. For local development, use the `.env.dev` (added to `.gitignore` by default), which overwrites the default configuration parameters. As a starting point, you can use the `env.dev.sample` file.

Optionally you can change the `topic.json` file to use your specific topic data. Have a look at the default `topic.json` (which represents the default data in the docker setup) to create your own config.

Optionally you can set a `swagger-descprition.md` to be shown on your Swagger OpenAPI page. If you don't want to create your own, the example swagger description markdown file will be used to generate it.

## Database

You need an accessible database connection for querying the test data. For the first version, a PostgreSQL (v15) database with the PostGIS extension is used. Sample data is stored in the `sql\data` dump and must be imported into your local database for testing.  
The database itself can be set up using three different approaches:

- Set up a database on your own. Follow one of the step-by-step tutorials for the initial configuration.
  - Please ensure that the database is accessible by your host. Do not forget to add needed parameters to `postgresql.conf` and `pg_hba.conf`
  - Do not forget to install the PostGIS extension:
    ```
    create extension postgis;
    ```
    And if you have problems with missing type 'raster':
    ```
    create extension postgis_raster;
    ```
  - Use psql, pg_restore, pgadmin or any other PostgreSQL client for importing the test data dump.
- You can also check the [installation guide](/documentation/postgresql-without-install.md) for setting up a PostgreSQL instance for missing administrator rights. The guide provides an easy step-by-step instructions for setting up the needed environment.
- Use the provided docker environment, which will create the needed database + extension + test data automatically.

### Add new database support

If you want to support another database, read more in [Database support](/documentation/database-support.md)

## Installation

Run the following command in your shell. This will download and install all needed dependencies and packages.

```bash
$ pnpm install
```

## Running the app

Run one of the following commands to start the service. The current scripts and parameters are defined in the `package.json` file.

Compile and run the service:

```bash
$ pnpm run start
```

Start the service in `watch mode` (more information [here](https://docs.nestjs.com/cli/usages#nest-start)), which adds live-reload and debugging functionalities. For more information about debugging check the corresponding section.

```bash
$ pnpm run start:dev
```

Compile the service for production usage. This does NOT start the actual service.

```bash
$ pnpm run start:prod
```

## Browser

Navigate to [http://localhost:3000/api](http://localhost:3000/api) to check out the SwaggerUI OpenAPI documentation.

Navigate to [http://localhost:3000/api-json](http://localhost:3000/api-json) to check out the SwaggerUI OpenAPI documentation in json format.

## Test

```bash
# unit tests
$ pnpm run test

# e2e tests
$ pnpm run test:e2e

# test coverage
$ pnpm run test:cov
```

## Docker

It is possible to run and develop this project with Docker or Podman. The `docker-compose.yml` development file will create an instance of the analysis-interface, a PostgreSQL database with PostGIS and some example data will be available. The data is imported from the dump in `sql/data` and the bounding box in decimal degrees (WGS84) is:

```
[50.952162, 13.666581],
[50.952162, 13.946723],
[51.066846, 13.946723],
[51.066846, 13.666581]
```

To comfortably check the database state, pgAdmin4 is included.

Two Dockerfiles are used to build images for dev or production environments. The compose files run containers based on these Dockerfiles.
The file structure is based on the following:

```
GeospatialAnalyzer/
├── docker-compose.yml              # Development
├── docker-compose-prod.yml         # Production
├── Dockerfile                      # Development image
├── Dockerfile-prod                 # Production image
```

### Docker Prerequisite

You need an installed and _running_ docker service. For example [Docker Desktop Windows](https://docs.docker.com/desktop/install/windows-install/).
Per default the database connection is set in the `docker-compose-(prod).yml` environment properties.
The docker-compose approach uses a specific docker network for encapsuling the services; the services are integrated with each other via the service names. In addition ports are exposed for accessing the application from outside.

### Run

Run:

```bash
docker compose up
```

Three containers (geospatialanalyzer-postgres-dev|prod, geospatialanalyzer-app-dev|prod, geospatialanalyzer-pgadmin-dev) will be created.

Changes inside the `src/` directory will be directly synced with the docker volume. So the backend-API always has the most current state.

### Dev / Prod container

To ensure that you use the developer container run:

```bash
docker compose -f docker-compose.yml up --build
```

If you want to run the production build, call:

```bash
docker compose -f docker-compose-prod.yml up --build
```

### Troubleshooting

If you update your `package.json`, change your docker files or have other problems that lead to a problematic start of your docker container; do the following: \
(<b> Beware, this will delete all manually added database data! </b>)

```bash
docker compose down -v
docker compose up --build
```

### Common Errors

```bash
/bin/bash^M: bad interpreter: No such file or directory
```

Check the corresponding file, e.g. `pg_restore.sh` and ensure that your IDE sets the line ending to `LF`. This is necessary, because our docker container uses
a Linux system. Especially for the database, other End of Line variations can lead to execution errors. :)

---

`ERROR [TypeOrmModule] Unable to connect to the database. Retrying (1)...`

Ensure, that you have edited your `.env` files. These files are synchronized, but are only read at the start of the application.
Therefore, you need to restart the container with `docker compose up`.

## PgAdmin4

Navigate to [http://localhost:5050](http://localhost:5050) to check out PgAdmin4.

To add to your local docker database:

- On the left-hand sidebar, click Servers to expand the Servers menu.
- Right-click on Servers and select Register -> Server.
- In the General tab of the Create - Server dialog, you can give the server a name of your choice.
- In the Connection tab, fill in the following details:
  - Host name/address: db
  - Port: 5432
  - Maintenance database: postgres
  - Username: postgres
  - Password: geobakery
- Click Save to save the server configuration.

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
