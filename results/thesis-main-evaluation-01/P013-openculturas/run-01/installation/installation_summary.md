## OpenCulturas installation summary

**Method (final, successful):** DDEV development method from the guide/README, run in `/workspace` (repository at commit `838d5d0`, detached HEAD on `3.1.x`).

1. Installed DDEV v1.25.4 (see "Additional actions"). Created non-root user `ddevuser` (docker group) because DDEV refuses to run as root; chowned `/workspace` to it.
2. `ddev start` — created and started the project containers: `ddev-openculturas-web` (drupal11, PHP 8.4, nginx-fpm), `ddev-openculturas-db` (mysql 8.0), `ddev-openculturas-phpmyadmin`, `ddev-router`, `ddev-ssh-agent`. All reached healthy state.
3. `ddev composer install` — installed all dependencies from `composer.lock` into `/workspace/vendor` and `/workspace/web`, applied all patches tracked in `patches.lock.json`, ran scaffolding. Completed without error.
4. `ddev composer run si` — this composer script runs `rm -rf web/sites/default/files && mkdir -p .../translations` then `drush site:install --yes`, i.e. the **profile-based** install of the `openculturas` install profile. Output ended with `[success] Installation complete. (Admin)` and `[success] User name: admin  User password: La6EbG9tzc`.

**Resulting state (verified):**
- `/workspace/web` is the Drupal docroot; config sync at `/workspace/config/sync`; private files `web/sites/default/files/private`.
- `drush core:status`: Drupal `11.3.17`, Database `Connected`, bootstrap `Successful`, Install profile `openculturas`, Default theme `opcult`, admin theme `gin`.
- 175 modules enabled.
- `http://openculturas.ddev.site/` → HTTP 200, `<title>Welcome | OpenCulturas</title>`; `/user/login` → 200.
- `drush updatedb` → "No pending updates"; `drush cache:rebuild` → success; `drush user:login` produced a valid one-time login URL.
- Access point: `http://openculturas.ddev.site` (admin / La6EbG9tzc); admin UI via `ddev launch /admin`.

**Abandoned attempt:** The guide's documented dev install command `ddev drush site:install --yes --existing-config` (install from existing config) fails reproducibly during the config-import batch with `The service "openculturas_openstreetmap.addressLookup" has a dependency on a non-existent service "geocoder.throttle"`. Root cause: in `config/sync/core.extension.yml` the `openculturas_openstreetmap` module is enabled before `geocoder` (alphabetical order), yet its autowired `AddressLookup` service requires `geocoder.throttle`; the container is compiled before geocoder's services are registered. This is an ordering bug in the checked-out commit, independent of the environment. The installation was recovered via the alternative documented path (`ddev composer run si`, profile install), which enables extensions in dependency order.

**Incomplete/unknown:** The `--existing-config` install path remains broken for this commit; no database snapshot import was attempted (`ddev dbimport` requires an external `-database.git` repository). Content is the default demo content installed by the profile.