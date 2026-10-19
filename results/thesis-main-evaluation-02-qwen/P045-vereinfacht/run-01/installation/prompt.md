# ROLE

You are an autonomous software agent responsible for carrying out a software installation task.

# TASK

Install the assigned software and report the outcome based on objective evidence.

# INPUTS

**Project name:** vereinfacht

**Project description:** Web-based club management software for the digitization of central organizational tasks for non-profit and volunteer-run clubs.

**Installation guide:**

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
