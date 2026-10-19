## Method
Installed IT-Fachplanung (PHP 8.3 + Smarty + MariaDB + OpenLDAP web app) in `/workspace` (ddev project `tfm-fachplanung`) following Installation.md, executing everything as non-root user `dev` (ddev refuses root; `dev` created and added to `docker` group). Working directory for all commands: `/workspace`.

## Prerequisite
The guide assumes a pre-installed ddev ("Es wird ein fertig installiertes ddev vorausgesetzt"), but none existed. Installed **ddev v1.25.4** (official GitHub release `ddev_linux-amd64.v1.25.4.tar.gz`) to `/home/dev/.local/bin/ddev`.

## Documented steps executed
1. `ddev start` — failed on first attempt: `ddev-tfm-fachplanung-openldap` container exited.
2. Diagnosed via `ddev logs -s openldap` + inspecting the `osixia/openldap:1.5.0` startup script: the image requires `chown -R`, `sed -i` (which renames the file), and (with `LDAP_REMOVE_CONFIG_AFTER_SETUP=true`) `rm -rf` on `assets/config/bootstrap/ldif/custom`, but the repo's `.ddev/docker-compose.ldap.yaml` mounted `test_users.ldif` there as a **single-file `:ro` bind mount** — incompatible (chown on RO fs; `sed -i` "Device or resource busy"; `rm` on a bind mount).
3. **Fix (only repo change):** in `.ddev/docker-compose.ldap.yaml`, replaced the single-file mount with a writable **directory** mount `../.ddev/ldap-seed:/container/service/slapd/assets/config/bootstrap/ldif/custom` (created `.ddev/ldap-seed/` containing a copy of `test_users.ldif`) and set `LDAP_REMOVE_CONFIG_AFTER_SETUP=false` (so the trailing `rm -rf assets/config` doesn't touch the bind mount). `KEEP_EXISTING_CONFIG` stays `false` (setting it `true` — an intermediate wrong attempt — silently skips the ldif bootstrap).
4. Used the guide's documented reset `ddev delete --omit-snapshot -y` + `ddev start` for a clean first start → all containers healthy.
5. `ddev composer install` — 47 packages installed to `vendor/`.
6. `ddev npm i` — `node_modules/` (451 entries).
7. `ddev importDump` — imported `dump/db.sql` (2022 dump) into DB `db`.
8. `cp config/web.config.local.php.example config/web.config.local.php`.

## Final state (verified)
- `ddev status`: **web** (PHP 8.3, docroot `public`), **db** (mariadb 10.3, db/db), **openldap**, **phpmyadmin** (host port 8036), **phpldapadmin** (host port 8076) all **OK**.
- LDAP: all **10 test users** (user1–user10) present under `ou=people,dc=example,dc=org` (verified with admin bind; anonymous search ACL-blocked → earlier "No such object" results were ACL noise, not missing data).
- DB: 9 tables — antragsbuch 0, dienststelle 53, dynform_field 166, fachplanung 106, gesamtplan 2, massnahme 817, teilmassnahme 4205, user 6, zweck 32.
- Compiled CSS/JS present in `public/theme/` (committed in git per the guide).
- Access points: `http://tfm-fachplanung.ddev.site/` (host-mapped `http://127.0.0.1:32789`); `/login` → 200, `/` → 302 to `/login`.

## End-to-end proof
Temporarily set a known bcrypt password on demo R1 user (id=1) via PHP, then `curl -d user=4874e97068325d2ec1c29b052bfd3a7f&pass=Test1234` POST `/login` → **302** to `/`; authenticated `GET /` with session → **200**, title "Startseite - IT-Fachplanung - Thüringen" with full R1 navigation (Antragsbuch, Berichte, Dienststellen, Dokumentation, Fachplanung, Gesamtplan). The original password hash was then restored and confirmed byte-identical.

## Known non-blocking test-data inconsistencies (not installation defects)
- `config/web.config.php` `ldap` block contains boilerplate values (`dc=planetexpress,dc=com`, bind `cn=Hubert J. Farnsworth,…`, host `ldap:10389`) that don't match the project's actual dev LDAP (`dc=example,dc=org`, hostname `openldap`, port 389; users lack the `description=Human` filter attribute). So the app's LDAP-validated login path won't work as-is without a local-config override — the DB/local-login path works (proven above).
- Bundled 2022 DB `user` table holds 6 UUID-named demo accounts with unpublished bcrypt passwords; no shared credentials with the 10 LDAP test users.

## Repo changes left in place
- `M .ddev/docker-compose.ldap.yaml` (the mount + `LDAP_REMOVE_CONFIG_AFTER_SETUP=false` fix; required for the LDAP container to start at all)
- `?? .ddev/ldap-seed/` (directory with a copy of `test_users.ldif` for the writable mount)
- Untracked/ignored artifacts: `vendor/`, `node_modules/`, `config/web.config.local.php`, ddev caches — all expected per `.gitignore` and the guide.