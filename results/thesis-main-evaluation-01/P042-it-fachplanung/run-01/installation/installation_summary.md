Installed IT-Fachplanung at commit 786839b in /workspace using DDEV (ddev v1.25.4, Docker 29.7.2, Ubuntu 22.04).

Steps:
1. Docker present, ddev absent. Installed ddev manually (verified GitHub release tarball ddev_linux-amd64.v1.25.4.tar.gz → /usr/local/bin) because the official installer refuses root.
2. Created non-root user `ddevuser` (uid 1000, docker group), chowned /workspace; run all ddev commands via `su - ddevuser -c`.
3. `ddev start`: initially the openldap container crash-looped because `.ddev/docker-compose.ldap.yaml` bind-mounted test_users.ldif as a single read-only file (chown/sed/rm failures). Fixed by mounting directory `.ddev/ldap-bootstrap/` and setting `LDAP_REMOVE_CONFIG_AFTER_SETUP=false`. All containers healthy.
4. `ddev composer install --no-interaction` (47 pkgs) — OK.
5. `ddev npm i` (592 pkgs) — OK.
6. `ddev importDump` from dump/db.sql — OK, 9 tables in db schema.
7. `cp config/web.config.local.php.example config/web.config.local.php`; aligned its LDAP block (host=openldap:389, dn=cn=admin,dc=example,dc=org, baseDn=dc=example,dc=org) to the LDAP service in the compose file, since the example referenced a stale planetexpress:10389 endpoint.
8. `ddev setup-docu-data` — OK.

Environment context: ddev project name `tfm-fachplanung`, docroot `public`, PHP 8.3, MariaDB 10.3, apache-fpm; containers ddev-tfm-fachplanung-{web,db,openldap,phpmyadmin,phpldapadmin}. Access at http://tfm-fachplanung.ddev.site. Commands must be run as user `ddevuser`; `ddev cypress` host command is unusable as-is, so Cypress was run directly with `cypress/included:13.17.0` attached to network ddev-tfm-fachplanung_default.

Verification: ddev describe shows web/db/openldap/phpmyadmin OK; HTTP `/`→302 and `/login`→200 with rendered login page; LDAP returns 10 users; Cypress specs 01-infrastruktur_setup (4/4) and 02-benutzerverwaltung (5/5, incl. LDAP search) pass. 030-fachplanung_erstellen had 1/3 fail due to expected 2027 test data not present — a doc-data ordering artifact, not an install defect.