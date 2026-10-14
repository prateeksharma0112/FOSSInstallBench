# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** vereinfacht

**Description:** Web-based club management software for the digitization of central organizational tasks for non-profit and volunteer-run clubs.

## Supplied installation guide

## Guide: Installation.md

# vereinfacht

**vereinfacht** is an open‑source, web‑based club management software, designed to digitize core organizational tasks for nonprofit and volunteer-based associations. It replaces paper forms and manual processes with flexible, multilingual online membership applications, customizable to each club's branding, structure, and member‑type needs. It includes an descriptive management interface and is built on an open source tools and dependencies, supporting smooth integration and self‑hosting at no cost.

This project still being actively developed and is in an early-adoption phase. It is is also [available as Software as a service](https://vereinfacht.digital/).

## Table of Contents

1. [Structure](#structure)
2. [Installation](#installation)
3. [Development](#swagger-api-docs)
4. [Development -> API](#api)
5. [Development -> API -> Swagger API docs](#swagger-api-docs)
6. [Development -> Web frontend](#web-frontend)
7. [Development -> Testing](#testing)
8. [License](#license)
9. [Contributing](#contributing)

## Structure

Inside this repository exist two applications required to run your own vereinfacht instance:
The Laravel API backend (`/api/`) and the Next.js web frontend (`/web_application/`).

### Core technologies

- Docker
- Laravel (API backend)
- JSON:API & Open API spec
- MariaDB
- Filament (admin panel)
- Next.js
- OpenAPI TypeScript
- Zod (schema validation)
- Tailwind CSS
- shadcn/ui component library
- Cypress (End-to-End testing)

## Development

### Development domains

| service                                | url                   |
| -------------------------------------- | --------------------- |
| web_application (tooling: npm run dev) | http://localhost:3000 |
| web_application (docker build)         | http://localhost:3003 |
| api                                    | http://localhost:3001 |
| swagger docs                           | http://localhost:3002 |

### API

The backend is a Laravel application using the [JSON:API](https://jsonapi.org/) specification. In order to adhere to the JSON:API specs, we use the package `laravel-json-api/laravel` as well as the package testing package `laravel-json-api/testing`. Refer to [the Laravel JSON:API docs](https://laraveljsonapi.io/4.x/) for more information.

#### Setup

First start the docker environment with `docker compose up -d`.
Then go into the tooling container:

```sh
docker compose exec tooling bash
cd api
composer install
cp .env.example .env
php artisan key:generate
php artisan migrate:fresh --seeder=FakeDatabaseSeeder
php artisan filament:assets
npm ci
npm run build
```

Aftwards create a token for the default super admin user:

```sh
php artisan tinker
```

```php
> User::find(1)->createToken('Super Admin Token')->plainTextToken;
```

Copy the generated token and supply it to the `/web_application/.env.local` file (see [web frontend](#web-frontend) setup below) as well as the `/e2e/cypress.config.ts`. If for any reason this token should change, remember to change it in those places as well.

You may now visit the login for the admin panel at [http://localhost:3001](http://localhost:3001) and use the seeded credentials for the super admin user:

```
Email: hello@vereinfacht.digital
Password: password
```

#### Swagger API docs

The Swagger API docs are available at the API URL via the path `/docs`. For local development this is [http://localhost:3002](http://localhost:3002).
Production API docs are available at [https://api.vereinfacht.digital/docs](https://api.vereinfacht.digital/docs).

The local API docs automatically use the API definition file stored in [`/api/public`](api/public/v1_openapi.json).

A new version of this file may be created with `php artisan jsonapi:openapi:generate v1` (requires the `FakeDatabaseSeeder` to be ran).

> [!NOTE]
> This process is **not** automated, because the generator package being used does not support all the specs / features the API needs.

The newly generated file can be found in `/api/storage/public`. For the time being you'll then have to manually copy over new additions to the previously mentioned and tracked file in [`/api/public`](api/public/v1_openapi.json). Remember to afterwards bump the version (`openapi.info.version`) of the specs accordingly:

```diff
{
    "openapi": "3.0.2",
    "info": {
        "title": "vereinfacht.digital JSON:API",
        "description": "JSON:API implementation for vereinfacht.digital",
-       "version": "0.0.1"
+       "version": "0.0.2"
    },
    ...
}
```

### Web frontend

#### Setup

If not already started, please start your docker environment with `docker compose up -d`.

Go into the tooling container:

```sh
docker compose exec tooling bash
cd web_application
cp .env.local.example .env.local
npm ci
```

Paste the API token mentioned in the previous API setup steps into the .env.local.

> [!WARNING]
> When running on production you should generate a new NextAuth secret (follow these steps: https://next-auth.js.org/configuration/options#secret).

Start the dev server while within the tooling container and inside `/web_application/`:

```sh
npm run dev
```

You may now visit the login for the club management at [http://localhost:3000](http://localhost:3000) and use the seeded credentials for the test user. For example:

```
Email: club-admin-1@example.org
Password: password
```

### Testing

#### Backend

Running the backend PHPUnit tests:

```sh
docker compose exec tooling bash
cd api
php artisan test
```

> [!NOTE]
> This repository does not yet include the End-to-End testing functionality described below. It will be included in the future.

#### End-to-End (web frontend)

We're using Cypress for End-to-End testing the web frontend areas of this project. Running tests successfully requires a database seeded with the `FakeDatabaseSeeder.php`, which is not being done automatically.

> [!WARNING]
> After running the Cypress End-to-End test suite, the database state is neither reset nor does it run with a separate testing database. This is different from the behavior of the PHPUnit tests in the `api` project. Keep that in mind when running the tests on your local copy of the application.

In order to use the component testing feature of Cypress, we would need to integrate Cypress into our Next.js application as an dependency. But then we're losing the option to test other parts of the mono repo in the future (i. e. a docs project or API pages). That's why Cypress was installed as a seperate project at the moment.

#### While developing

To run the tests, you'll first need to run a development process of the web_application app from the tooling container and make sure, the project is reachable under http://localhost:3000. Afterwards you can run the tests headlessly by entering `npm run test` from the `e2e` container:

```sh
docker exec -it verein_e2e bash
npm run test
```

#### Using the Cypress GUI

If you have node installed globally on the host machine, you can use the Cypress GUI while writing, debugging and running your tests (**highly recommended**). First, you have to follow these steps from your host machine:

```sh
cd /e2e
npm install
npx cypress install
```

After successfully installing Cypress as described above, you can run `npm run open` within the `/e2e` folder. You may also have to setup the host of the api on your machine in order to allow the Cypress GUI to make api requests.

In order to use the GUI within the docker container, additional steps are required and this project isn't setup for that now. More about this: https://www.cypress.io/blog/2019/05/02/run-cypress-with-a-single-docker-command/

#### Testing a frontend build

You can also test the current frontend build by changing the `baseUrl` value via the config flag to `http://web_application:3000` (see `./e2e/package.json`).

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

## Method
Installed via Docker Compose from `/workspace` at commit `c2a2b2e`. The `vereinfacht` compose stack was built and started, then the Laravel API and Next.js frontend were configured following the supplied guide.

## Key actions & state
- **Images built**: `vereinfacht-api:latest`, `vereinfacht-web_application:latest`, `vereinfacht-tooling:latest` (plus pulled `mariadb:11.8`, `docker.swagger.io/swaggerapi/swagger-ui`).
- **Containers running** (`docker compose ps`): `vereinfacht-database-1` (3306), `vereinfacht-api-1` (3001→80), `vereinfacht-api-docs-1` (3002→8080), `vereinfacht-tooling-1` (3000), `vereinfacht-web_application-1` (3003→3000).
- **Blocking bug fixed**: `docker/tooling/tooling.Dockerfile` had `COPY --from=node /usr/lib /usr/lib`, which replaced the PHP image's newer `libapk.so.3.0.0` (apk-tools 3.0.8) with node image's older copy (apk-tools 3.0.6), breaking `apk` inside later RUN steps (`Error relocating /sbin/apk: apk_fs_is_malicious_filename: symbol not found`, exit 127). The line was commented out; `docker compose build tooling` then succeeded.
- **API setup** (all inside `vereinfacht-tooling-1`, working dir `/var/www/html/api`): `composer install`; `cp .env.example .env`; `php artisan key:generate`; `php artisan migrate:fresh --seeder=FakeDatabaseSeeder`; `php artisan filament:assets`; `npm ci`; `npm run build`; super-admin token created with `php artisan tinker`.
- **Web setup**: `cp .env.local.example .env.local` (in `/var/www/html/web_application`) with the API bearer token; `npm ci`; `npm run dev` started in the tooling container on port 3000.
- **Permission fix**: `chown -R 1000:1000 api/storage api/bootstrap/cache` on the host — php-fpm worker runs as uid 1000 (`verein`) while files were root-owned, causing HTTP 500 on every request.
- **Compose tweak**: added `env_file: ./web_application/.env.local` and `API_DOMAIN`/`NEXTAUTH_URL` to the `web_application` service so the dockerized build (port 3003) works (previously next-auth `NO_SECRET` 500).

## Access points
- API/admin: http://localhost:3001 (admin login `hello@vereinfacht.digital` / `password`)
- Swagger docs: http://localhost:3002
- Web dev frontend: http://localhost:3000 (test user `club-admin-1@example.org` / `password`)
- Dockerized web frontend: http://localhost:3003

## Files changed in repo
`docker/tooling/tooling.Dockerfile` and `docker-compose.yml`. Local runtime config (`api/.env`, `web_application/.env.local`) and dependency dirs are gitignored. No incomplete work; the Cypress `e2e` project referenced by the guide is absent from the repository.

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