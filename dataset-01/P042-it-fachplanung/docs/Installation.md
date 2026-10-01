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
