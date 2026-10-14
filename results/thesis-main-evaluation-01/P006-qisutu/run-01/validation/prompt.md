# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** Qisutu

**Description:** Open-source service desk for ticket management, customer portal, automation, knowledge base, CMDB and REST API.

## Supplied installation guide

## Guide: Installation.md

# Qisutu installieren

## Voraussetzungen

- ein unterstütztes Linux-System
- root-Zugriff für die Systemvorbereitung
- Netzwerkzugriff auf die Paketquellen des Betriebssystems
- ein Installationspfad ohne Leerzeichen

Empfohlene und vollständig unterstützte Referenzplattform ist Ubuntu Server
LTS. Zusätzlich besitzt der Installer eigene Installationswege für:

- Debian
- RHEL, Rocky Linux, AlmaLinux, CentOS und Fedora
- openSUSE und SLES

Andere Distributionen werden nicht stillschweigend wie Ubuntu behandelt. Das
Installationsskript bricht dort mit einer eindeutigen Meldung ab.

## 1. Archiv entpacken

Jede Qisutu-Instanz benötigt ein eigenes Hauptverzeichnis.

Beispiele:

    /opt/qisutu
    /opt/qisututest

Für ein Testsystem muss das entpackte Verzeichnis daher vor der Installation
beispielsweise `/opt/qisututest` heißen. Der Verzeichnisname ist gleichzeitig
die vollständige Instanzkennung; der Installer ergänzt kein Präfix.

## 2. Systemvorbereitung starten

Im Hauptverzeichnis der betreffenden Instanz ausführen:

    sudo ./install.sh

Als erste Installationsangabe wird eine der elf unterstützten Sprachen
ausgewählt. `install.sh` speichert diese Auswahl in
`var/install/instance.conf`. Der anschließende Webinstaller erscheint bereits
in der gewählten Sprache und verwendet sie als voreingestellte
Standardsprache für Qisutu.

### Normale Installation

Liegt Qisutu im empfohlenen Verzeichnis `/opt/qisutu`, nimmt das Skript alle
Instanzwerte automatisch. Es werden keine technischen Namen abgefragt.
Automatisch verwendet werden unter anderem:

    Webpfad:          /qisutu
    Apache-Datei:     qisutu.conf
    systemd-Dienst:   qisutu-daemon.service
    Session-Cookie:   QISUTU_SESSION
    Datenbank:        qisutu
    Datenbankbenutzer:qisutu

### Zusätzliche Test- oder Entwicklungsinstanz

Jede weitere Instanz wird in ein eigenes Verzeichnis entpackt, zum Beispiel:

    /opt/qisututest

`install.sh` übernimmt den Verzeichnisnamen unverändert als vollständige
Instanzkennung. Alle technischen Namen werden unmittelbar daraus erzeugt:

    Instanzkennung:   qisututest
    Webpfad:          /qisututest
    Apache-Datei:     qisututest.conf
    systemd-Dienst:   qisututest-daemon.service
    Session-Cookie:   QISUTUTEST_SESSION
    Datenbank:        qisututest
    Datenbankbenutzer:qisututest

Der Verzeichnisname muss mit einem Kleinbuchstaben beginnen und darf höchstens
24 Kleinbuchstaben, Zahlen oder Bindestriche enthalten. Bei Bindestrichen
verwendet nur MariaDB technisch notwendige Unterstriche. Ein zusätzliches
`qisutu-`-Präfix wird niemals erzeugt.

Die automatisch ermittelten Werte werden in `var/install/instance.conf`
gespeichert. Bei späteren Aufrufen von `install.sh` wird eine vollständig
installierte Instanz nicht verändert. Bei einer noch nicht abgeschlossenen
Installation werden veraltete, vom früheren Installer erzeugte Präfixe sicher
an den tatsächlichen Verzeichnisnamen angepasst.

Das Skript installiert Apache, MariaDB beziehungsweise MySQL-Clientwerkzeuge,
Perl und die benötigten Perl-Module einschließlich `Authen::SASL` und
`Net::LDAP`. Nach der Paketinstallation prüft es alle benötigten Mail-,
Verzeichnis- und Datenbankmodule.

Die Apache-Konfiguration wird distributionsabhängig eingebunden:

- Debian und Ubuntu: `sites-available/INSTANZ.conf` und Aktivierung über
  `sites-enabled/` mit `a2ensite`
- RHEL, Rocky Linux, AlmaLinux, CentOS und Fedora:
  `/etc/httpd/conf.d/INSTANZ.conf`
- openSUSE und SLES: `/etc/apache2/conf.d/INSTANZ.conf`

Jede Instanz erhält außerdem eigene systemd-Dateien. Dadurch können
beispielsweise folgende Dienste parallel laufen:

    qisutu-daemon.service
    qisututest-daemon.service

Auf Systemen der RHEL-Familie richtet das Skript bei aktivem SELinux die
notwendigen Dateikontexte und SELinux-Schalter für CGI-, Datenbank- und
Netzwerkverbindungen ein. Ist `firewalld` aktiv, wird HTTP freigegeben.

Auf lokalen MariaDB-Installationen erzeugt das Skript pro Instanz einen
temporären, zufällig gesicherten Datenbank-Installationsbenutzer. Der
Webinstaller entfernt ihn nach erfolgreicher Datenbankeinrichtung wieder.

## 3. Webinstaller ausführen

Die von `install.sh` ausgegebene Adresse im Browser öffnen.

Produktivbeispiel:

    http://SERVER/qisutu/install.pl

Testbeispiel:

    http://qisututest.qisutu.de/qisututest/install.pl

Der Assistent führt durch:

1. Willkommen, Instanzdaten und Systemprüfung
2. Lizenzbestätigung
3. Datenbank und Grunddaten
4. Systemeinstellungen einschließlich Protokoll und FQDN
5. optionale IMAP-/SMTP-Konfiguration
6. Abschluss und erste Zugangsdaten

Datenbankname und Datenbankbenutzer stammen aus der zuvor festgelegten
Instanzkonfiguration und werden im Webinstaller nicht mehr eigenmächtig
geändert. Der Installer erzeugt zufällige Passwörter für den jeweiligen
Datenbankbenutzer und den ersten Benutzer `admin`. Das Datenbankpasswort wird
direkt in `core/config/QisutuConfig.pm` dieser Instanz gespeichert.

Die vollständige Tabellenstruktur wird aus `install/sql/schema.sql` importiert.
Alle festen Grunddaten der Neuinstallation stehen getrennt davon in
`install/sql/insert.sql`. Das zufällig erzeugte Administratorpasswort wird nach
dem Grunddatenimport sicher gehasht in das vorbereitete Administratorkonto
eingetragen.

## 4. Abschluss

Nach Abschluss wird innerhalb der betreffenden Instanz
`var/install/installed.lock` angelegt. Damit ist ausschließlich der Installer
dieser Instanz gesperrt. Der eigene systemd-Pfad aktiviert danach den zu dieser
Instanz gehörenden Qisutu-Daemon.

Beispielzugänge:

    http://SERVER/qisutu/index.pl
    http://qisututest.qisutu.de/qisututest/index.pl

## LDAP / Active Directory für Agenten und Kundenbenutzer

Die Verzeichnisanmeldung wird nach der Installation ausschließlich durch einen
Administrator unter `Administration > LDAP / Active Directory` konfiguriert.
Dort stehen zwei vollständig getrennte Profile bereit:

- `Agenten-LDAP` ausschließlich für Anmeldungen im Agentenportal
- `Kunden-LDAP` für Kundenbenutzer und ihre Kundenunternehmen

Jedes Profil besitzt eine eigene Verbindung, Suche, Feldzuordnung, Prüfung und
Aktivierung. In den Anmeldemasken gibt es keine Auswahl zwischen lokaler
Anmeldung und Active Directory; Qisutu verwendet anhand des Portals automatisch
das passende aktive Profil.

Für beide Profile sind anzugeben:

- Verzeichnistyp, Server, Port und LDAPS oder StartTLS
- optional ein technisches Suchkonto sowie eine eigene CA-Datei
- Benutzer-Base-DN und zusätzlicher Benutzerfilter
- die verpflichtenden LDAP-Attribute für Login, Vorname, Nachname und E-Mail

Das Agentenprofil kann zusätzlich eine Standardgruppe für automatisch neu
angelegte Agenten und Mappings für weitere Agentenfelder enthalten. Das
Kundenprofil benötigt zusätzlich je ein LDAP-Attribut für die eindeutige
Qisutu-Kundennummer und den Namen des Kundenunternehmens. Weitere
Kundenbenutzerfelder können ebenfalls mit LDAP-Attributen verbunden werden.
Zusatzfelder, die in Qisutu als erforderlich definiert sind, benötigen im
jeweiligen Profil zwingend ein Mapping und einen Wert im Verzeichnis.

Das Serverzertifikat wird standardmäßig gegen den Zertifikatsspeicher des
Betriebssystems geprüft. Das Bind-Passwort wird verschlüsselt abgelegt. Ein
gespeichertes oder geändertes Profil bleibt zunächst inaktiv. Mit einem
Test-Login werden Suche und alle Pflicht-Mappings geprüft; mit einem optionalen
Test-Passwort zusätzlich die echte Benutzeranmeldung. Erst ein erfolgreicher
Test erlaubt die Aktivierung des betreffenden Profils.

Beim Agentenlogin sucht Qisutu mit dem eingegebenen Wert, übernimmt danach aber
den kanonischen Wert aus dem konfigurierten Login-Attribut. Ein vorhandener
Qisutu-Agent mit diesem Login wird weiterverwendet und auf LDAP-Anmeldung
umgestellt; andernfalls wird ein neuer Agent angelegt. Ein E-Mail-Treffer wird
nicht zum Zusammenführen verwendet.

Beim Kundenlogin wird das Kundenunternehmen über die gemappte Kundennummer
gefunden oder neu angelegt. Der Kundenbenutzer wird anhand des kanonischen
Logins gefunden oder angelegt und diesem Unternehmen zugeordnet. Ändert sich
die gemappte Kundennummer, wird eine frühere aktive Unternehmenszuordnung des
Kundenbenutzers deaktiviert. E-Mail-Konflikte mit einem anderen Kundenkonto
brechen die automatische Anlage oder Aktualisierung ab.

Findet das jeweils aktive Verzeichnis keinen Benutzer, kann ein bestehendes
lokales Konto weiterhin lokal angemeldet werden. Sobald ein eindeutiger
Verzeichniseintrag gefunden wurde, ist dessen Passwortprüfung maßgeblich und es
gibt keinen Rückfall auf ein lokales Passwort. LDAP-Konten sind von der lokalen
Passwort-vergessen-Funktion ausgeschlossen. Wird für ein Konto ausdrücklich ein
neues lokales Passwort vergeben, wird es wieder auf lokale Authentifizierung
umgestellt.

## Mehrere Instanzen auf demselben Server

Jede Instanz benötigt nur ein eigenes Hauptverzeichnis. Aus `/opt/qisutu`
und `/opt/qisututest` erzeugt das Installationsskript automatisch getrennte
Webpfade, Apache-Dateien, systemd-Dienste, Session-Cookies, Datenbanken und
Datenbankbenutzer. Diese internen Werte müssen nicht vom Benutzer eingegeben
werden.

E-Mail-Zugänge des Testsystems müssen von den produktiven Postfächern getrennt
bleiben. Die E-Mail-Konfiguration kann bei der Testinstallation übersprungen
werden.

## Eingehende E-Mail-Konten und OAuth2

Nach der Installation werden eingehende E-Mail-Konten im Administrationsbereich
über den Menüpunkt `E-Mail-Abruf` verwaltet. Die Übersicht zeigt alle vorhandenen
Konten und bietet oben die drei Einrichtungsarten an:

- `Standard-IMAP` verwendet Benutzername und Passwort.
- `Microsoft 365` verwendet OAuth2/XOAUTH2 mit
  `outlook.office365.com` auf Port 993.
- `Google Workspace/Gmail` verwendet OAuth2/XOAUTH2 mit
  `imap.gmail.com` auf Port 993.

Für Microsoft 365 oder Google Workspace/Gmail ist zuerst unter
`Administration > System-Einstellungen` die öffentliche Qisutu-Basis-URL mit
HTTPS einzutragen, zum Beispiel `https://support.example.org/qisutu`. Qisutu
zeigt daraus in der Anlegemaske die vollständige OAuth2-Weiterleitungs-URI an.
Diese URI muss im Microsoft-Entra- beziehungsweise Google-Cloud-Projekt exakt
als erlaubte Web-Redirect-URI registriert werden.

### Microsoft 365

Im Microsoft-Entra-Anwendungsprojekt werden eine Client-ID und ein
Client-Secret benötigt. Als Tenant-ID kann die konkrete Verzeichnis-ID oder
`common` verwendet werden. Qisutu fordert den IMAP-Scope
`https://outlook.office.com/IMAP.AccessAsUser.All` sowie `offline_access` an.
Das zu verbindende Microsoft-Konto muss Zugriff auf das angegebene Postfach
besitzen und IMAP muss für das Postfach erlaubt sein.

### Google Workspace/Gmail

Im Google-Cloud-Projekt wird ein OAuth-Client vom Typ Webanwendung mit
Client-ID und Client-Secret benötigt. Qisutu fordert den Scope
`https://mail.google.com/` und Offline-Zugriff an. Der OAuth-Zustimmungsbildschirm
muss für das verwendete Konto freigegeben sein. Bei Google-Workspace-Domänen
kann zusätzlich eine Freigabe durch die Administration erforderlich sein.

Nach `Speichern und mit OAuth2 verbinden` führt Qisutu durch die Anmeldung beim
Anbieter. Erst nach erfolgreichem Token-Austausch und echtem IMAP-Test wird das
Konto aktiviert. Access-Tokens werden beim späteren Mailabruf automatisch mit
dem gespeicherten Refresh-Token erneuert. Client-Secrets und Tokens dürfen
nicht in Protokolle, Supportausgaben oder öffentliche Fehlerberichte kopiert
werden.

Ein inaktives Konto wird beim erneuten Aktivieren zuerst durch einen echten
Verbindungstest geprüft. Die vollständige Löschung ist nur bei inaktiven
Konten möglich und muss in einem Bestätigungsdialog nochmals bestätigt werden.
Zugangsdaten und OAuth2-Tokens werden dabei entfernt. Bereits vorhandene
Postmaster-Verarbeitungsprotokolle bleiben als Historie erhalten, verlieren
aber die Verknüpfung zum gelöschten Konto.

## Ausgehender SMTP-Versand und OAuth2

Unter `Administration > SMTP settings` stehen drei getrennte Einrichtungsarten
zur Verfügung:

- `Standard-SMTP` verwendet Benutzername und Passwort.
- `Microsoft 365` verwendet `smtp.office365.com`, Port 587, STARTTLS und
  OAuth2/XOAUTH2 mit `offline_access` sowie
  `https://outlook.office.com/SMTP.Send`.
- `Google Workspace/Gmail` verwendet `smtp.gmail.com`, Port 587, STARTTLS und
  OAuth2/XOAUTH2 mit `https://mail.google.com/`.

Für OAuth2 wird wie beim IMAP-Abruf eine Webanwendung beim jeweiligen Anbieter
benötigt. Die in der SMTP-Kontomaske angezeigte Redirect-URI muss dort exakt
registriert sein. Nach dem Speichern führt Qisutu zur Anmeldung beim Anbieter,
speichert Access- und Refresh-Token verschlüsselt und führt einen echten
SMTP-Test mit `AUTH XOAUTH2` aus. Nur bei erfolgreichem Test wird das Konto
aktiviert. Access-Tokens werden bei Bedarf automatisch erneuert. Die Aktionen
`Neu verbinden` und `OAuth-Verbindung trennen` verwalten die lokale
Token-Verbindung; beim Trennen wird das SMTP-Konto sofort deaktiviert.

## Öffentliche Webformulare einbetten

Formulare werden nach der Installation unter `Administration > Formulare`
verwaltet. Bei einem öffentlichen Formular zeigt Qisutu den Direktlink und
einen fertigen Iframe-Code an. Voraussetzung für eine absolute URL ist die
öffentliche HTTPS-Basis-URL unter `Administration > System-Einstellungen`.

Unter `Erlaubte Einbettungs-Domains` sollte jede erlaubte Website vollständig
und zeilenweise eingetragen werden, zum Beispiel:

    https://www.example.org
    https://service.example.org

Der Wert `*` erlaubt die Einbettung auf jeder Domain und sollte nur bewusst
verwendet werden. Qisutu setzt daraus die CSP-Direktive `frame-ancestors`.
Zusätzlich lassen sich Grenzwerte pro IP und Stunde, pro IP und Tag sowie ein
Gesamtlimit pro Tag festlegen. Der öffentliche Einstieg liegt innerhalb des
Instanz-Webpfads unter `form.pl?Form=URL-KENNUNG`.

Öffentliche Webformulare erstellen keine Kunden, Ansprechpartner oder
Benutzerkonten. Die Tickets bleiben zunächst ohne Kundenzuordnung; Name und
E-Mail-Adresse des Absenders werden im Artikel und im Formular-Snapshot
aufbewahrt. Kunden und Ansprechpartner werden regulär in der Administration
angelegt. Formulare im angemeldeten Kundenportal verwenden weiterhin den
bereits vorhandenen Kunden und Ansprechpartner. Formularübermittlungen bleiben
als Snapshot am Ticket erhalten und werden bei späteren Formularänderungen
nicht verändert.

Beim regulären Update werden eindeutig erkennbare, unveränderte
Webformular-Platzhalter aus früheren Ständen entfernt. Tickets und
Formular-Snapshots bleiben erhalten. Die freigegebenen Login- und
E-Mail-Adressen können danach für vollständig neue Ansprechpartner verwendet
werden.

## Protokolle

Jede Instanz besitzt ihr eigenes Installationsprotokoll:

    var/log/install.log

Passwörter werden nicht in das Installationsprotokoll geschrieben.

## Systembenutzer und Dateirechte

Qisutu verwendet für Hintergrundprozesse den Systembenutzer `qisutu`. Der
Installer legt diesen Benutzer bei Bedarf an und nimmt ihn in die Gruppe des
Webservers auf. Auf Ubuntu und Debian gehören die Installation und ihre
beschreibbaren Laufzeitverzeichnisse deshalb `qisutu:www-data`.

Der instanzbezogene Daemon läuft ebenfalls als `qisutu` und ruft die
eingerichteten Postfächer automatisch alle fünf Minuten ab. Ein zusätzlicher
Cronjob für `qisutu-mail-fetch.pl` ist nicht erforderlich. Gemeinsame
Runtime-Lockdateien unter `/run/lock/qisutu` sind für `qisutu` und die
Webserver-Gruppe beschreibbar und werden nach einem Neustart automatisch mit
den richtigen Rechten wiederhergestellt. Eine eigene instanzbezogene
Mailabruf-Sperre verhindert parallel laufende Abrufe.

## Temporäre Abschlussdienste

Während der Webinstallation wartet eine instanzbezogene systemd-Path-Unit auf `var/install/installed.lock`. Nach erfolgreichem Abschluss startet die zugehörige einmalige Service-Unit den Qisutu-Daemon. Anschließend werden beide temporären Abschluss-Units automatisch deaktiviert und aus `/etc/systemd/system` entfernt. Dauerhaft aktiv bleibt ausschließlich der jeweilige Qisutu-Daemon.
## Updates einer vorhandenen Qisutu-Instanz

Vor jedem Update muss entsprechend der Betreiberanweisung eine vollständige
Systemsicherung der Qisutu-Installation und ihrer Datenbank vorhanden sein.
Qisutu erstellt keine zusätzliche Programmsicherung.

Zur Systemsicherung gehört insbesondere `var/secure/security.key`. Dieser
installationsabhängige Schlüssel wird nicht in der Datenbank gespeichert und
wird benötigt, um verschlüsselte E-Mail- und OAuth-Zugangsdaten sowie
Zwei-Faktor-Geheimnisse wiederherzustellen. Der Schlüssel darf nur zusammen
mit einer geschützten Sicherung aufbewahrt und niemals veröffentlicht werden.

Ein neues Qisutu-Release wird in ein separates Verzeichnis entpackt. Das neue
Paket darf nicht direkt über die bestehende Installation entpackt werden.
Anschließend wird `update.sh` aus dem neuen Paket mit dem Pfad der zu
aktualisierenden Instanz aufgerufen.

Produktivinstanz aktualisieren:

    cd /tmp/qisutu-neue-version/qisutu
    sudo ./update.sh /opt/qisutu

Zusätzliche Instanz aktualisieren:

    cd /tmp/qisutu-neue-version/qisutu
    sudo ./update.sh /opt/qisututest

Das Updateprogramm liest die vorhandene `var/install/instance.conf` und zeigt
vor der Bestätigung Installationspfad, Instanzkennung, Webpfad, Datenbank und
systemd-Dienst an. Es aktualisiert ausschließlich die angegebene Instanz.

Während des Updates führt das Programm folgende Schritte aus:

1. Release-Prüfsummen, Versionen, Schemadatei, Perl-Syntax und
   Programmregistrierung prüfen.
2. Auf Wunsch einen zusätzlichen vollständigen Datenbankdump erstellen und auf
   den dafür erforderlichen freien Speicherplatz hinweisen.
3. Für genau diese Instanz den Wartungsmodus aktivieren, den Daemon stoppen,
   laufende Prozesse beenden lassen und neue Mailabrufe sperren.
4. Alle verwalteten Programmdateien direkt in die bestehende Installation
   kopieren. Vorhandene Dateien werden ersetzt, neue Dateien und Verzeichnisse
   werden angelegt und nicht mehr veröffentlichte verwaltete Dateien entfernt.
5. Instanz- und Betreiberdateien unverändert erhalten. Dazu gehören
   `core/config/QisutuConfig.pm` mit Ausnahme der Versionsnummer,
   `var/install/instance.conf`, Logs, Cache, temporäre Laufzeitdaten,
   `var/secure/security.key`, instanzbezogene Runtime-Dateien, die bestehende
   Apache-Konfiguration und die bestehende systemd-Konfiguration.
6. Die aktuelle Datenbank-Sollstruktur aus `install/sql/schema.sql` mit der
   vorhandenen Datenbank vergleichen und fehlende Tabellen, Spalten, Indizes,
   Primärschlüssel und Fremdschlüssel ergänzen.
7. Alle dauerhaft mitgeführten und noch nicht protokollierten SQL- und
   Perl-Migrationen aus `install/update/database/` ausführen. Dadurch werden
   auch notwendige `INSERT`-, `UPDATE`- und Datenumwandlungsschritte unabhängig
   von der bisherigen Qisutu-Version nachgeholt.
8. Schema, Migrationsprotokoll, Datenbankstand, Programmdateien,
   Betreiberkonfigurationen, Apache und Daemon prüfen.
9. Wartungsmodus beenden und den zuvor laufenden Daemon wieder starten.

Der Updater baut keinen zweiten Qisutu-Programmbaum auf, verschiebt keine
Installationsverzeichnisse und legt keine automatische Programmsicherung an.
Bei einem Fehler nach begonnenen Datei- oder Datenbankänderungen bleibt die
Wartungssperre aktiv. Nach Behebung des gemeldeten Fehlers wird dasselbe Update
erneut ausgeführt.

Die vorhandenen Apache-Dateien und Symlinks unter `sites-available`,
`sites-enabled`, `conf-available` und `conf-enabled` sowie der vorhandene
systemd-Dienst unter `/etc/systemd/system` werden nicht neu erzeugt und nicht
überschrieben. Der Updater prüft ausdrücklich, dass ihr Inhalt und ihre
Dateieigenschaften unverändert geblieben sind.

Die aktuelle Tabellenstruktur wird bei jedem Update mit
`install/sql/schema.sql` abgeglichen. Zusätzliche bestehende Tabellen oder
Spalten werden nicht gelöscht. Abweichende vorhandene Definitionen werden aus
Sicherheitsgründen gemeldet und nicht automatisch destruktiv geändert.

Einmalige Datenänderungen wie `INSERT`, `UPDATE` oder Datenumwandlungen liegen
kumulativ unter:

    install/update/database/DATENBANKVERSION/

Alle veröffentlichten `.sql`- und `.pl`-Migrationen bleiben dauerhaft in jedem
späteren Updatepaket enthalten. Jede Migration muss so programmiert sein, dass
sie den bereits vorhandenen Datenzustand prüft und bei Bedarf nur die fehlenden
Daten ergänzt oder umwandelt. Die Tabelle `database_migration` protokolliert jede Datei unter ihrem dauerhaft
eindeutigen Migrationsschlüssel und speichert zusätzlich ihre Prüfsumme.
Nicht protokollierte Migrationen werden immer in aufsteigender Reihenfolge
ausgeführt; bereits protokollierte Migrationen werden anhand ihres Schlüssels
nicht erneut ausgeführt. Danach wird nochmals die vollständige Sollstruktur
geprüft und erst dann der aktuelle Stand in `database_version` eingetragen.

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

Installed Qisutu 2.0.2 from /workspace to /opt/qisutu per INSTALL.md. Ran `QISUTU_INSTALL_LANGUAGE=de bash ./install.sh` (exit 0), which installed Apache2, MariaDB, Perl modules (incl. Authen::SASL, Net::LDAP), created the qisutu system user, generated var/secure/security.key, wrote var/install/instance.conf, deployed /etc/apache2/sites-available/qisutu.conf (symlinked to sites-enabled), and installed /etc/systemd/system/qisutu-daemon.service plus temporary install-complete units. Then executed the browser web installer over HTTP on http://localhost/qisutu/install.pl through all six steps (welcome/system check, license, database, system settings, mail skipped, completion). It created MariaDB database `qisutu` with 138 tables (schema.sql + insert.sql), DB user `qisutu`, first admin user `admin`, wrote core/config/QisutuConfig.pm, and created var/install/installed.lock. Verified: index.pl HTTP 200, authenticated login HTTP 302 with dashboard, api.pl HTTP 401 (unauthenticated), Apache/MariaDB running, qisutu-daemon.pl running as user qisutu, ownership of program tree qisutu:www-data. Environment note: the container has tini as PID 1 with no systemd; a minimal /usr/local/bin/systemctl shim was created to map start/stop/enable/is-active to the Apache/MariaDB services so the documented installer could run, and the daemon was started directly with the completion units applied manually. Files live at /opt/qisutu; login at http://localhost/qisutu/index.pl (admin / PLEUTQQVHW7G3ED+C7PN%%LK).

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