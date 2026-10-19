# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** IT-Fachplanung

**Description:** More efficient IT departmental planning for the highest state authorities and their business units.

## Supplied installation guide

## Guide: Installation.md

# IT-Fachplanung

Die Software mit angebundener Datenbank soll die Erstellung, Änderung, Prüfung und Aus-wertung der IT-Fach- und Gesamtplanung sowohl für die Ressorts, deren Geschäftsbereiche als auch der KS E-Gov-IT effizienter, zuverlässiger und flexibler machen.

Ziel ist es, mit dem neu zu entwickelnden System den obersten Landesbehörden und deren Geschäftsbereichen sowie dem Rechnungshof des Freistaats Thüringen zu einer wesentlich effizienteren IT-Ressortplanung zu verhelfen und Mehrfachentwicklungen/ -beschaffungen zu vermeiden.

## Ersteinrichtung
Es wird ein fertig installiertes ddev vorausgesetzt.

``` bash
git clone git@gitlab.opencode.de:thlv/it-fachplanung.git
cd it-fachplanung

ddev start 
ddev composer install
ddev npm i

# Datenbank-Dump laden (dump/db.sql, import Stand 2022)
ddev importDump
cp config/web.config.local.php.example config/web.config.local.php
```

## LDAP-Einrichtung
Für die Entwicklung sind 10 Testbenutzer in der Datei `test_users.ldif` vorkonfiguriert. Diese werden beim ersten Start des LDAP-Containers automatisch geladen.

Um die Benutzer zu laden oder zu aktualisieren:
```bash
# Neustart des Containers (falls bereits konfiguriert)
ddev restart

# Falls der LDAP-Container bereits Daten enthält und die User nicht erscheinen,
# müssen die LDAP-Volumes zurückgesetzt werden (Achtung: Datenverlust im LDAP!):
ddev delete --omit-snapshot -y
ddev start
```

## Build-Set (CSS/JS)

Compiliertes CSS und Javascript wird in GIT "händisch" hinzugefügt.

Konfiguration: siehe ``Gulpfile.js``

```bash
# CSS und Js (ddev exec gulp build)
ddev build
# zusätzlich Plugins (ddev exec gulp buildAll)
ddev buildAll

# Watcher (ddev exec gulp dev)
ddev dev
ddev watch
```

## Dev-Tools

``` bash
### php-cs-fixer (Optimiert php-Code, Empfehlung vorher "git add app", damit man die Ändeurngen besser vergleichen kann
# Aufruf kurz:
ddev fixPhp
# führt folgendes aus:
ddev exec vendor/bin/php-cs-fixer fix app

### rector ist auch verwendbar:
ddev exec vendor/bin/rector process app --dry-run
```


## Deployment des letzten aktuellen Standes
Vorbereitung:
- eigener SSH-Key muss auf dem UAT-Server installiert sein
```bash
ssh-copy-id ***REMOVED***
```

Deployment:
```bash
ddev auth ssh
ddev surf deploy current
```

## SBOM aktualisieren
Dies ist nötig, wenn Dependencies in composer oder npm aktualisiert werden.
```
ddev composer sbom:create
git add sbom/
git commit -m "[TASK] updated SBOM"
```

http://tfm-fachplanung.ddev.site/

# Dokumentation  

https://tfm-fachplanung.ddev.site/dokumentation

Die Dokumentation wird automatisiert erstellt. Um die Testdaten und Screenshots konsistent zu generieren, sollte der kombinierte Befehl genutzt werden, der vor jedem Test-Lauf die Datenbank automatisch zurücksetzt:

```bash
# Gesamte Dokumentationsbilder generieren (alle Tests)
ddev cypress run

# Gezielt einzelne Workflows dokumentieren
ddev cypress run --spec "cypress/e2e/02-benutzerverwaltung.cy.js"
ddev cypress run --spec "cypress/e2e/030-fachplanung_erstellen.cy.js"
```

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

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