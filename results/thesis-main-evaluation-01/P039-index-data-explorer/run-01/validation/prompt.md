# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** Index Data Explorer

**Description:** Open-source web application for analyzing and visualizing multidimensional data from Elasticsearch indices.

## Supplied installation guide

## Guide: Installation.md

## Installation

#### Basic idea

The _Index Data Explorer_ is a web application, written in HTML and Javascript. So everything you need on the endusers computer is a modern web browser (like e.g. Firefox or Chromium)

##### Prerequisites:
 - WebServer (linke e.g. Apache or Nginx)
 - Elasticsearch Service
 
##### Steps:
 - Add the following folders from toplevel of the project to the document root folder of the webserver or a subdirectory of your choice:
   + config
   + externalPackages
   + i18n
   + src
   + php (* only needed, if the computer running the browser has no acccess to the used Elasticsearch service *)
   + Additionally you need a folder _data_ on toplevel for specific instances, e.g. for some pages in _examples/kosis_
 - copy the HTML pages you want to offer in _your_ Explorer instance to the same folder of the webserver
 - Note: all the HTML pages on toplevel or in one of the folders in subfolder _examples_ can be copied to the document root folder and are functional there (that is: will find their used/imported files like CSS or images or configuration files)
 - Note: check the _examples_ directory to see some proper use cases
 - Adjust the values in the config files used by your HTML pages to the correct index name(s) and base URL. Additionally you can overwrite the default configurations of most javascript modules found in subfolder _src_ in the config files.

For more detailed information refer to the wiki page mentioned above.

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

Installed the Index Data Explorer static web application at /workspace (git commit a8c4210).

Method: The app is static HTML/JS with all libraries vendored in externalPackages/, so no build/package install is required. Following the guide's "copy folders to the webserver document root" instructions, I served the repository toplevel directly as the nginx document root, making the required folders (config, externalPackages, i18n, src, php) and all HTML pages available.

Actions:
1. `apt-get update` then `DEBIAN_FRONTEND=noninteractive apt-get install -y python3 nginx` (nginx 1.18.0, python3 from Ubuntu 22.04 repos).
2. Wrote /etc/nginx/sites-available/daexp with `listen 8080`, `root /workspace`, `index index.html`, `try_files $uri $uri/ =404`; symlinked into sites-enabled; removed the default site.
3. Validated with `nginx -t` (success) and started nginx (master PID 1328).

Paths: repo/document root = /workspace; nginx site config = /etc/nginx/sites-available/daexp; executable = /usr/sbin/nginx.

Access point: http://localhost:8080/index.html plus example pages under /examples/.

State: nginx is running and serves all app assets. No Elasticsearch service was installed; config/baseConfig.json points at http://localhost:9200, so live data querying requires an Elasticsearch instance (and optionally php/dataExplorerProxy.php) at runtime. The optional top-level `data` folder used by some example instances already exists inside examples/*/data.

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