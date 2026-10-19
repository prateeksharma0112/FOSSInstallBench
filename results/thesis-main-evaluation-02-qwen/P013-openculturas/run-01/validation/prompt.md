# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** OpenCulturas

**Description:** Event calendar and cultural platform with profiles, magazine, interactive maps

## Supplied installation guide

## Guide: Installation.md

## Requirements
* https://www.drupal.org/docs/system-requirements for Drupal
  * PHP 8.4
* A bunch of drupal modules and external libraries.

## Installation

### New installation

Use the composer project template:

```bash
composer create-project --remove-vcs drupal/openculturas_project example.org
```

For more information go to https://www.drupal.org/project/openculturas_project.

### Updating

#### Patch release

Optionally update library versions in the inline package repositories in `composer.json`, then:

```bash
composer update openculturas/openculturas-distribution "drupal/core-*" drupal/core --with-dependencies --minimal-changes
drush updatedb --yes
# Review changes, then export and commit configuration
drush config:export --yes
```

#### Minor release

Manually increase the version constraints for `drupal/core-*` and `openculturas/openculturas-distribution` to the next minor version in `composer.json`, then follow the same steps as a patch release.


## Development

Please read the [Development guidelines](DEVELOPMENT.md) before you start.

We recommend using https://ddev.com for development.

### Installation (with ddev)

* Clone this repository
* Install dependencies
  * `ddev composer install`
* Install OpenCulturas distribution
  * `ddev drush site:install --yes --existing-config`

### DDEV

Cheatsheet:

* Start project `ddev start`
* Run composer commands `ddev composer COMMAND` e.g. `ddev composer install`
* Run drush commands `ddev drush COMMAND` e.g. `ddev drush uli`
* Import latest database snapshot `ddev dbimport`

More information about ddev cli command https://ddev.readthedocs.io/en/stable/users/basics/cli-usage/.

### Patching

Patches are managed with [cweagans/composer-patches](https://docs.cweagans.net/composer-patches/) v2 and tracked in `patches.lock.json`.

```bash
ddev composer patches-relock   # Re-discover patches in composer.json and rewrite patches.lock.json
ddev composer patches-repatch  # Delete, re-download and re-apply patches for all affected packages
ddev composer patches-doctor   # Diagnose common patching issues
```

Run `patches-relock` after adding or removing a patch in `composer.json`. Run `patches-repatch` when a patch fails to apply or a package needs a clean re-install.

### PHP Quality Checks

```bash
ddev composer run php:lint        # PHP parallel lint
ddev composer run php:cs          # PHPCS
ddev composer run php:cs-fix      # Auto-fix PHPCS issues
ddev composer run php:phpstan     # Static analysis
ddev composer run php:rector      # Rector dry-run
ddev composer run php:rector-fix  # Rector auto-fix
```

### JS/CSS Linting

All linting commands run inside the DDEV container:

```bash
ddev exec npm run lint:js         # ESLint JavaScript (entire project)
ddev exec npm run lint:yaml       # ESLint YAML
ddev exec npm run lint:css        # stylelint CSS (profile/modules)
ddev exec npm run lint:css:fix    # Auto-fix CSS
ddev exec npm run lint:scss       # stylelint SCSS (openculturas_base theme)
ddev exec npm run lint:scss:fix   # Auto-fix SCSS
ddev exec npm run prettier        # Prettier JavaScript
ddev exec npm run prettier:css    # Prettier CSS
ddev exec npm run prettier:scss   # Prettier SCSS
```

To lint specific JS files:

```bash
ddev exec npx eslint --ext .js --no-ignore path/to/file.js
```

### Configuration files

All configurations are managed via [config_devel](https://www.drupal.org/project/config_devel).
Each configuration is listed in the info file of the profile or module.
Therefore, any changes to the configuration must also be made in the info file.

After that, enable config_devel and run `ddev composer run cde` or `ddev drush cde module`.

This command updates all configuration listed in the info file and removes the key `_core` and `uuid` except for
views configuration. The uuid is needed because the uuid is used in other configuration as a default value, without this
the default value would be not set/broken.

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

## What was done

The workspace `/workspace` contains the checked-out **openculturas-distribution** repository (a DDEV `drupal11` project; docroot `web`, PHP 8.4, MySQL 8.0). The goal was to install the OpenCulturas distribution.

### Environment preparation
- The container (Ubuntu 22.04, root, Docker 29.7.2) had **no** PHP, Composer, Node, or ddev.
- Installed **ddev v1.25.4** from the official GitHub release (checksum verified). DDEV refuses to run as root, so a non-root user `dev` (docker group) was created and `/workspace` was chowned to it; ddev commands are run via `runuser -u dev -- ddev ...`.
- Separately, PHP 8.4.26 + Composer 2.10.3 were installed on the host (ondrej PPA) to run the documented `composer create-project` method.

### Installation (primary — DDEV, the checked-out repo)
1. `ddev start` — pulled/built project images, started web + db containers (PHP 8.4.24, MySQL 8.0.46).
2. `ddev composer install --no-interaction` — installed all 333 locked dependencies (vendor/ and web/ populated; scaffold + patches applied).
3. `ddev drush site:install --yes --existing-config` (the guide's documented command) — **FAILED**:
   `The service "openculturas_openstreetmap.addressLookup" has a dependency on a non-existent service "geocoder.throttle"` (exit 1).

### Root cause (verified in core + repo source)
With `--existing-config`, Drupal skips the profile's module-install task and instead imports `config/sync`, enabling every module in `config/sync/core.extension.yml` one-by-one in dependency-weight order, calling `ModuleInstaller::install($names, FALSE)` (dependencies NOT auto-enabled). `openculturas_openstreetmap` is listed in `core.extension.yml` (line 119); its `AddressLookup` autowires `geocoder.throttle` (from the `geocoder` module), but its `.info.yml` declares dependencies only on `ctools`, `key`, `oauth2_client` — **not** `geocoder`. `geocoder` is a zero-dependency leaf (lowest weight), so `openculturas_openstreetmap` is enabled first and the container rebuild fails. This is a genuine missing module-dependency bug in the committed dev snapshot.

### Fix applied (one line)
Added `- 'geocoder:geocoder'` to `profile/modules/custom/openculturas_openstreetmap/openculturas_openstreetmap.info.yml` (the standard Drupal remedy). This resolved the `geocoder.throttle` error, but the `--existing-config` path then hit a **second, distinct** committed-config import error (`Call to a member function getSettings() on null in Drupal\Core\Field\FieldConfigBase`), i.e. the dev snapshot's committed `config/sync` has further latent import issues. The exact `--existing-config` command therefore cannot complete at this commit without re-exporting the committed config.

### Recovery → completed install
Ran the documented install command in its base form, `ddev drush site:install --yes` (fresh install from the `openculturas` distribution profile). It **completed successfully** (`Installation complete`, admin user `admin` created). This is a working install of the checked-out OpenCulturas distribution.

### Alternate documented method (independent)
`composer create-project --remove-vcs drupal/openculturas_project example.org` **succeeded**, producing a full project at `/workspace/example.org` (released `openculturas-distribution` ~3.1.3; its install list does not enable the experimental openstreetmap module, so it is unaffected by the bug). Composer dependencies are installed there; the site itself was not further installed in that copy.

### Final state / access points
- Site: `http://openculturas.ddev.site` (also `http://localhost/en`); start with `ddev start`; drush via `ddev drush ...` (as `dev` user). Admin login via `ddev drush uli`.
- Working-tree changes: the one-line `openculturas_openstreetmap.info.yml` dependency fix, plus untracked `/workspace/example.org`. `web/core` is untouched.

Known caveats: the exact `ddev drush site:install --yes --existing-config` command is broken at this commit by the committed `config/sync` (missing `geocoder` dependency + a field-config import error); a fresh `site:install --yes` was used instead and fully works.

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