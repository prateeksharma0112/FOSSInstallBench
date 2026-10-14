# ROLE

You are an autonomous software agent responsible for carrying out a software installation task.

# TASK

Install the assigned software and report the outcome based on objective evidence.

# INPUTS

**Project name:** IT-Fachplanung

**Project description:** More efficient IT departmental planning for the highest state authorities and their business units.

**Installation guide:**

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
