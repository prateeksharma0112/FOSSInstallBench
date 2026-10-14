# ROLE

You are an autonomous software agent responsible for carrying out a software installation task.

# TASK

Install the assigned software and report the outcome based on objective evidence.

# INPUTS

**Project name:** Erlebnis.Stadt Menden

**Project description:** Web app with experiences from the city of Menden

**Installation guide:**

## Guide: Installation.md

# Menden CMS Backend

Source: [backend/README.md](https://gitlab.opencode.de/stadt-menden/erlebnis.stadt/-/blob/e5a8336a130b9e379db54b4b8d6fa21cfd38dd58/backend/README.md)

## Requirements

Before you begin, please ensure you have the following installed:

* [Docker](https://www.docker.com/products/docker-desktop)
* [JDK 21](https://jdk.java.net/21/) (required only if you are not using Docker to run the Spring application.)
* **GitHub Personal Access Token**: Required to access certain dependencies hosted in the GitHub Packages repository.

### Why a GitHub Token is Required

The application depends on certain Maven packages hosted in a private GitHub Packages repository. To authenticate and
download these dependencies, a GitHub Personal Access Token is necessary. The token can be set either in the environment
or directly in the build configuration file.

#### Example Maven Configuration:

```kotlin
repositories {
    mavenCentral()
    maven {
        url = uri("https://maven.pkg.github.com/sw-code/Urbo")
        credentials {
            username = "" // Your GitHub username (can remain empty)
            password = System.getenv("GITHUB_TOKEN") ?: "your-github-token" // The GitHub token
        }
    }
}
```

### How to Set the GitHub Token

You can set the token in one of the following ways:

1. **Set the token in the build script**:
    - Open the `buildSrc/src/main/kotlin/io/swcode/menden/common-conventions.gradle.kts` file and set the token
      directly:
    ```kotlin
    repositories {
        mavenCentral()
        maven {
            url = uri("https://maven.pkg.github.com/sw-code/Urbo")
            credentials {
                username = "" // Your GitHub username (can remain empty)
                password = "your-personal-access-token" // Replace with your token
            }
        }
    }
    ```

2. **Set the token as an environment variable**:
    - Export the token in your terminal session:
    ```shell
    export GITHUB_TOKEN=your-personal-access-token
    ```

## Setting Up Docker

1. **Docker Setup**: Before running the application, start the necessary Docker containers:

    * Navigate to the `/docker` directory:

    ```shell
    cd docker
    ```

    * To start the containers without the Spring application:

    ```shell
    docker-compose up
    ```
   > **Caution:** Ensure Docker containers are completely started and all services are up before proceeding to run the
   application. Some services might take longer to initialize, so be patient.


2. **Running the Application**: You have two options:
    * **Using Your IDE**:
        * Locate the class `io.swcode.menden.cms.app.MendenCmsApplication`.
        * Execute the `main` method within the class.

    * **Using Gradle**:
        * Run the application using the Gradle wrapper command:

    ```shell
    ./gradlew :menden-app:bootRun
    ```

---

# AngularMonorepo

Source: [app/README.md](https://gitlab.opencode.de/stadt-menden/erlebnis.stadt/-/blob/e5a8336a130b9e379db54b4b8d6fa21cfd38dd58/app/README.md)

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Node.js (version 20.17.0 or higher) installed
- pnpm (version 9.12.3 or higher) installed
- Nx CLI `nx` installed (`pnpm install -g nx`)

### Prerequisites for Using Private GitHub Packages

This project uses private packages hosted on the **GitHub Package Registry**. To install dependencies and work with these private packages, you'll need to authenticate with GitHub using a **Personal Access Token (PAT)**. This token is required to grant your system permission to access the private registry.

#### Why is this needed?

- Private packages are stored in the GitHub Package Registry, which requires authentication for access.
- The **Personal Access Token (PAT)** allows the package manager to authenticate with GitHub securely.
- Without this token, you will encounter errors like `403 Forbidden` or `404 Not Found` when trying to install packages.

---

#### How to Set Up Authentication

There are two ways to provide the authentication token:

---

#### 1. Add It to Your `.npmrc` File

Add the following lines to the root-level `.npmrc` file of your workspace or your user-level `.npmrc` file (`~/.npmrc`):

```

strict-peer-dependencies=false
auto-install-peers=true

@sw-code:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
```

**Note:** Replace `${GITHUB_TOKEN}` with your actual GitHub **Personal Access Token** if you're not using an environment variable.

---

#### 2. Set It as an Environment Variable

Alternatively, you can define the `GITHUB_TOKEN` environment variable on your system. This method is more secure since the token is not stored in plaintext on disk.

- On **Windows**:

  ```
  setx GITHUB_TOKEN your_personal_access_token
  ```

- On **macOS/Linux**:

  ```
  export GITHUB_TOKEN=your_personal_access_token
  ```

Make sure the environment variable is accessible in the shell or terminal session where you're running Nx commands.

---

#### Verify Setup

Once the token is configured, run the following command to verify it works:

```
pnpm install
```

If the setup is correct, the dependencies should install without errors. If you encounter issues, ensure:

- Your token has the correct permissions (`read:packages` and optionally `repo` for private repos).
- The `.npmrc` or environment variable is correctly configured.

## Run tasks

To run the dev server for your app, use:

```sh
pnpm nx serve erlebnis.stadt
```

To create a production bundle:

```sh
pnpm nx build erlebnis.stadt
```

To see all available targets to run for a project, run:

```sh
pnpm nx show project erlebnis.stadt
```

These targets are either [inferred automatically](https://nx.dev/concepts/inferred-tasks?utm_source=nx_project&utm_medium=readme&utm_campaign=nx_projects) or defined in the `project.json` or `package.json` files.

[More about running tasks in the docs &raquo;](https://nx.dev/features/run-tasks?utm_source=nx_project&utm_medium=readme&utm_campaign=nx_projects)

---

# Cms

Source: [cms/README.md](https://gitlab.opencode.de/stadt-menden/erlebnis.stadt/-/blob/e5a8336a130b9e379db54b4b8d6fa21cfd38dd58/cms/README.md)

## Run tasks

To run the dev server for your app, use:

```sh
pnpm start
```

These targets are either [inferred automatically](https://nx.dev/concepts/inferred-tasks?utm_source=nx_project&utm_medium=readme&utm_campaign=nx_projects) or defined in the `project.json` or `package.json` files.

[More about running tasks in the docs &raquo;](https://nx.dev/features/run-tasks?utm_source=nx_project&utm_medium=readme&utm_campaign=nx_projects)

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
