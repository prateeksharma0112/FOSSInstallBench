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