<a id="installation"></a>
# Installationsanleitung

In den nachfolgenden Abschnitten wird die Installation der einzelnen Komponenten erläutert.

<a id="installationskomponenten"></a>
## Überblick der Installationskomponenten

Die xPlanBox umfasst die folgenden Komponenten, die zusammengenommen die Liefereinheit darstellen. Speichern Sie die Distributionsdatei in einem lokalen Verzeichnis und entpacken Sie die ZIP-Datei. Prüfen Sie die Vollständigkeit der Distributionsdatei anhand der folgenden Auflistung.

| *Komponente* | *Konfigurationen* | *Beschreibung* |
| --- | --- | --- |
| xplan-dokumente-api.war | xplan-dokumente-config.zip | xplandokumente-api |
| xplan-manager-web.war | xplan-manager-config-default.zip, xplan-manager-workspace.zip | xplanmanager-web |
| xplan-manager-api.war | xplan-manager-config-default.zip, xplan-manager-workspace.zip | xplanmanager-api |
| xplan-services-wfs-syn.war | xplan-services-wfs-syn-workspace.zip | xplanwfs |
| xplan-services-wfs.war | xplan-services-wfs-workspace.zip | xplanwfs |
| xplan-services-wms.war | xplan-services-wms-workspace.zip | xplanwms |
| xplan-validator-web.war | xplan-validator-config.zip, xplan-validator-workspace.zip | xplanvalidator-web |
| xplan-validator-api.war | xplan-validator-config.zip, xplan-validator-workspace.zip | xplanvalidator-api |
| xplan-validator-executor.jar | - | xplanvalidator-executor |
| xplan-webpages.war | - | xplanresources |
| xplan-webservices-inspireplu.war | xplan-webservices-inspireplu-workspace.zip | xplaninspirepluwfs,xplaninspirepluwms |
| xplan-webservices-validator-wms.war | xplan-webservices-validator-wms-workspace.zip | xplanvalidator-wms |
| xplan-cli.zip | - | xplanclitools |
| externe Komponente | xplan-mapserver-config.zip | Konfiguration für MapServer |
| externe Komponente | xplan-mapproxy-config.zip | Konfiguration für MapProxy |
| externe Komponente | xplan-ldproxy-config.zip | Konfiguration für ldproxy |
| externe Komponente | xplan-database-scripts.jar | Liquibase Changelog-Dateien für XPlanDB |
| xplan-benutzerhandbuch-html.zip | - | Benutzerhandbuch für die Komponenten der xPlanBox in HTML-Format |
| xplan-benutzerhandbuch-pdf.zip | - | Benutzerhandbuch für die Komponenten der xPlanBox |
| xplan-betriebshandbuch-html.zip | - | Betriebshandbuch für die Komponenten der xPlanBox in HTML-Format |
| xplan-betriebshandbuch-pdf.zip | - | Betriebshandbuch für die Komponenten der xPlanBox in PDF-Format |

> **Note:** Stellen Sie vor Beginn der Installation sicher, dass die Distributionsdatei vollständig ist. Bitte kontaktieren Sie [lat/lon GmbH](https://www.lat-lon.de), per E-Mail an info@lat-lon.de, wenn Installationskomponenten fehlen.

<a id="vorbereitung-der-installation"></a>
## Vorbereitung der Installation

Die folgende Installationsanleitung setzt voraus, dass die im Abschnitt systemueberblick beschriebenen Komponenten, soweit erforderlich, installiert sind.

<a id="installation-directories"></a>
### Verzeichnisse für die Konfigurationsdateien

Weiterhin ist vorbereitend das Anlegen von Verzeichnissen erforderlich, in dem die Konfigurationsdateien abgelegt werden können:

- `DEEGREE_WORKSPACE_ROOT`: Der Pfad zu diesem Verzeichnis muss über die Umgebungsvariable `DEEGREE_WORKSPACE_ROOT` (Vorgabewert ist das Verzeichnis *.deegree/* im Home-Verzeichnis des Nutzers, z. B. unter Linux */home/user/.deegree*) gesetzt werden. In diesem Verzeichnis werden die Konfigurationsdateien für die XPlanDienste abgelegt. Beispiel: `DEEGREE_WORKSPACE_ROOT=/opt/deegree`.
- `XPLANBOX_CONFIG`: Der Pfad zu diesem Verzeichnis muss über die Umgebungsvariable `XPLANBOX_CONFIG` (Vorgabewert ist das Verzeichnis *xplanbox/* im Home-Verzeichnis des Nutzers, z. B. unter Linux */home/user/xplanbox/*) gesetzt werden. In diesem Verzeichnis werden die Konfigurationsdateien für die XPlanManager und XPlanValidator abgelegt. Beispiel: `XPLANBOX_CONFIG=/opt/xplanbox/xplan-manager-config/`.

> **Important:** Dem Betriebssystembenutzer, mit dem der Tomcat-Server gestartet wird, müssen Lese- und Schreibrechte für das Verzeichnis `DEEGREE_WORKSPACE_ROOT` eingeräumt werden.

<a id="installation-umgebungsvariablen"></a>
### Umgebungsvariablen

Neben den beiden genannten Verzeichnissen können auch andere Konfigurationen über Umgebungsvariablen gesetzt werden. Die Anwendungskomponenten der xPlanBox nutzen folgenden Umgebungsvariablen:

```text
DEEGREE_WORKSPACE_ROOT
XPLANBOX_CONFIG
XPLAN_DB_HOSTNAME
XPLAN_DB_PORT
XPLAN_DB_NAME
XPLAN_DB_USER
XPLAN_DB_PASSWORD
XPLAN_DB_INIT_USER
XPLAN_DB_INIT_PASSWORD
XPLAN_MAX_ERRORS_GEOMETRIC_VALIDATION
XPLAN_MAX_PLANS_XPLANGML
XPLAN_RABBIT_HOST
XPLAN_RABBIT_PASSWORD
XPLAN_RABBIT_USER
XPLAN_RABBIT_PUBLIC_TOPIC
XPLAN_RABBIT_PUBLIC_TOPIC_ROUTINGPREFIX
XPLAN_RABBIT_PRIVATE_ANONYMOUSQUEUES_PREFIX
XPLAN_RABBIT_PRIVATE_TOPIC
XPLAN_RABBIT_PRIVATE_TOPIC_ROUTINGPREFIX
XPLAN_RABBIT_PRIVATE_WORKQUEUE_IMPORT
XPLAN_RABBIT_PRIVATE_WORKQUEUE_VALIDATION
XPLAN_S3_ACCESS_KEY
XPLAN_S3_SECRET_ACCESS_KEY
XPLAN_S3_REGION
XPLAN_S3_ENDPOINT
XPLAN_S3_BUCKET_ATTACHMENTS
XPLAN_S3_BUCKET_MAPPROXYCACHE
XPLAN_S3_BUCKET_VALIDATION
XPLAN_S3_PATHSTYLEACCESS_ENABLED
XPLAN_VALIDATION_TIMEOUT
```

Sollen XPlanValidator und XPlanManager mehr als 500 Planobjekte je XPlanGML-Datei verarbeiten können, dann kann über die Umgebungsvariable `XPLAN_MAX_PLANS_XPLANGML` die Anzahl der maximalen Objekte geändert werden. Wird dieser Wert erhöht, dann muss insbesondere der Komponente XPlanValidatorExecutor ausreichend Arbeitsspeicher und CPU zugewiesen werden. Hinweise dazu stehen im Abschnitt monitoring-capacity-planing.

Soll der Abbruch der geoemtrischen Validierung im XPlanValidator und XPlanManager nach mehr als 250 Fehlern und Warnungen erfolgen, dann kann über die Umgebungsvariable `XPLAN_MAX_ERRORS_GEOMETRIC_VALIDATION` die maximale Anzahl an Geometriefehlern und -warnungen erhöht werden.

Die Umgebungsvariablen für Datenbank, S3 und RabbitMQ werden in den folgenden Abschnitten dokumentiert.

<a id="s3-storage"></a>
### S3-Objektspeicher einrichten

Für die Ablage von Rasterdateien, Begleitdokumenten und Validierungsreports ist ein S3-Objektspeicher erforderlich. Neben Cloud-Anbietern von S3-kompatiblen Objektspeichern können auch die Komponenten des Open Source Projekts [SeaweedFS](https://github.com/seaweedfs/seaweedfs) verwendet werden.

> **Important:** Folgende S3-Objektspeicher konnten erfolgreich mit der xPlanBox getestet werden: AWS S3, IONOS S3, Hetzner S3, DELL OneFS, MinIO, Ceph Storage sowie SeaweedFS. Nicht kompatibel war zum Zeitpunkt der Release-Erstellung die Implementierung von: Ontap S3.

#### Konfiguration des S3-Objektspeichers

Die Ablage von Rasterdaten, Begleitdokumenten und Validierungsreports sowie der optionale Cache erfordert getrennte Buckets. Für die xPlanBox müssen mehrere Buckets angelegt werden:

1. [Attachments](#s3-storage-attachments): Beinhaltet alle Rasterdaten und Begleitdokumente zu den Planwerken
2. [Validation](#s3-storage-validation): Beinhaltet die Validierungsreports mit den Validierungsergebnissen
3. [MapProxyCache](#s3-storage-mapproxy): Beinhaltet die gekachelten Rasterdaten für den XPlanMapProxy (optional)

Für die Komponenten der xPlanBox müssen die Angaben für den S3-Objektspeicher über Umgebungsvariablen gesetzt werden:

```properties
XPLAN_S3_ACCESS_KEY=MY_ACCESS_KEY <1>
XPLAN_S3_SECRET_ACCESS_KEY=MY_SECRET_KEY <2>
XPLAN_S3_REGION=eu-central-1 <3>
XPLAN_S3_ENDPOINT=s3.eu-central-1.amazonaws.com <4>
XPLAN_S3_PATHSTYLEACCESS_ENABLED=true <5>
```
**1:** Zugangsdaten zum S3-Speicher: Accesskey
**2:** Zugangsdaten zum S3-Speicher: Secretkey
**3:** S3-Region in der die Buckets liegen
**4:** S3-Endpoint URL mit Protokoll oder Hostname ohne Angabe des Protokolls
**5:** Aktivierung der Angabe des Namens des S3-Bucket im Pfad anstatt als virtueller Host

> **Note:** Der S3-Nutzer benötigt Lese- und Schreibberechtigungen für alle drei Buckets.

<a id="s3-storage-attachments"></a>
#### S3-Objektspeicher für Rasterdaten und Begleitdokumente

Rasterdaten werden zusammen mit den Begleitdokumenten in einem S3-Objektspeicher gespeichert. Die Rasterdaten werden über den XPlanMapServer abgerufen. Die Begleitdokumente können über die XPlanDokumenteAPI abgerufen werden.

Dazu müssen in den [Tomcat-Instanzen](#konfiguration-der-applikationsserver) mit xplanmanager-web und xplanmanager-api die Verbindungsdaten für S3-API über Umgebungsvariablen gesetzt werden. Für den MapServer steht in dem Distributionspaket *xplan-mapserver-config-<VERSION>.zip* eine Konfigurationsdatei *mapserver.map* bereit. In dieser Datei müssen die Angaben für `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_S3_ENDPOINT` (siehe [AWS CLI Umgebungsvariablen](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html)) angepasst werden.

> **Tip:** Weitere Informationen zur Konfiguration des [S3](https://aws.amazon.com/de/s3/) Objektspeichers im MapServer [Mapfile](https://mapserver.org/mapfile/map.html) und [GDAL Virtual File Systems](https://gdal.org/user/virtual_file_systems.html).

**Name des S3-Objektspeichers für Rasterdaten und Begleitdokumente**
```properties
XPLAN_S3_BUCKET_ATTACHMENTS=myattachmentsbucket <1>
```
**1:** Hier muss der Name des S3-Bucket für die Rasterdaten und Begleitdokumente gesetzt werden, hier als Beispiel `myattachmentsbucket`.

> **Tip:** Die S3-Versionierung kann für diesen Bucket aktiviert sein.

<a id="s3-storage-validation"></a>
#### S3-Objektspeicher für Validierungsreports

Für die Ablage von Validierungsreports im S3-Objektspeicher muss folgende Umgebungsvariable gesetzt werden:

**Name des S3-Objektspeichers für Validierungsreports**
```properties
XPLAN_S3_BUCKET_VALIDATION=myvalidationreportbucket <1>
```
**1:** Hier muss der Name des S3-Bucket für die Validierungsreports gesetzt werden, hier als Beispiel `myvalidationreportbucket`.

> **Tip:** Für das Validierungsreports-Bucket wird empfohlen, eine Lebenszyklusrichtlinie (S3 lifecycle policy) mit `--expire-days "30"` anzulegen, damit alte Validierungsreports automatisch gelöscht werden.

> **Note:** Die S3-Versionierung kann für diesen Bucket aktiviert sein, wird aber nicht empfohlen.

<a id="s3-storage-mapproxy"></a>
#### S3-Objektspeicher für MapProxy-Cache

Für die Ablage des MapProxy-Caches im S3-Objektspeicher muss folgende Umgebungsvariable gesetzt werden:

**Name des S3-Objektspeichers für MapProxy-Cache**
```properties
XPLAN_S3_BUCKET_MAPPROXYCACHE=mymapproxycachebucket <1>
```
**1:** Hier muss der Name des S3-Bucket für die Ablage der Kacheln (Tiles) gesetzt werden, hier als Beispiel `mymapproxycachebucket`.

> **Note:** Die S3-Versionierung sollte für diesen Bucket deaktiviert sein.

<a id="installation-rabbitmq"></a>
### Installation und Konfiguration von RabbitMQ

Die xPlanBox nutzt für die interne Kommunikation zwischen den Komponenten den Message Broker [RabbitMQ](https://www.rabbitmq.com/). Die Installation von RabbitMQ ist in der [Dokumentation](https://www.rabbitmq.com/docs/download) beschrieben.

In RabbitMQ müssen für die interne Kommunikation zum Austausch von Nachrichten zwischen XPlanManagerAPI/XPlanValidatorAPI und XPlanValidatorExecutor zwei [Quorum Queues](https://www.rabbitmq.com/docs/quorum-queues) eingerichtet werden. Für die Quorum Queues muss ein [Delivery Acknowledgement Timeout](https://www.rabbitmq.com/docs/consumers#acknowledgement-timeout) (`consumer-timeout`, Vorgabewert: 30 Minuten) gesetzt sein, das größer ist als das Validation Timeout der xPlanBox (`XPLAN_VALIDATION_TIMEOUT`, Vorgabewert: 15 Minuten). Zusätzlich sollte in RabbitMQ für die Quorum Queues eine Policy gesetzt sein, dass das `delivery-limit` auf  `1` (Vorgabewert: 20) setzt. Dadurch wird sichergestellt, dass eine Validierung nur einmal wiederholt wird, wenn diese aufgrund von Fehlern fehlschlägt. Optional kann für die Kommunikation mit externen Komponenten noch ein Topic eingerichtet werden.

Für die Kommunikation der Anwendungskomponenten XPlanManagerAPI, XPlanValidatorAPI und XPlanValidatorExecutor müssen die folgenden Umgebungsvariablen gesetzt sein:

```properties
XPLAN_RABBIT_HOST=localhost <1>
XPLAN_RABBIT_USER=xplanbox <2>
XPLAN_RABBIT_PASSWORD=xplanbox <3>
XPLAN_RABBIT_PUBLIC_TOPIC=latlon.xplanbox.public <4>
XPLAN_RABBIT_PUBLIC_TOPIC_ROUTINGPREFIX=xplanbox. <5>
XPLAN_RABBIT_PRIVATE_ANONYMOUSQUEUES_PREFIX=latlon.xplanbox.private- <6>
XPLAN_RABBIT_PRIVATE_TOPIC=latlon.private <7>
XPLAN_RABBIT_PRIVATE_TOPIC_ROUTINGPREFIX=xplanbox. <8>
XPLAN_RABBIT_PRIVATE_WORKQUEUE_IMPORT=latlon.xplanbox.private.import <9>
XPLAN_RABBIT_PRIVATE_WORKQUEUE_VALIDATION=latlon.xplanbox.private.validation <10>
XPLAN_VALIDATION_TIMEOUT=900000 <11>
```
**1:** Host-Adresse von RabbitMQ
**2:** Zugangsdaten für RabbitMQ: Benutzername
**3:** Zugangsdaten für RabbitMQ: Passwort
**4:** Name des Topic für den Datenaustausch mit externen Komponenten
**5:** Prefix für Routingkey für den Datenaustausch mit externen Komponenten über das Topic
**6:** Prefix für Queues für den Datenaustausch mit internen Komponenten (API v1)
**7:** Name des Topic für den Datenaustausch mit internen Komponenten
**8:** Prefix für Routingkey für den Datenaustausch mit internen Komponenten
**9:** Name der Queue für den Import
**10:** Name der Queue für die Validierung
**11:** Validation Timeout in Millisekunden

<a id="installation-liquibase"></a>
### Installation von Liquibase

Für die initiale Installation von Liquibase sind folgende Schritte erforderlich:

- Download und Installation von Liquibase wie in der [Dokumentation](https://docs.liquibase.com/start/install/home.html) beschrieben.
- Nach der Installation sollte der Aufruf von `liquibase --version` möglich sein:
```bash
export LIQUIBASE_HOME=/path/to/liquibase-5.0.1
$LIQUIBASE_HOME/liquibase --version
```

<a id="konfiguration-der-datenbank"></a>
## Erstellen der Datenbank XPlanDB

<a id="konfiguration-xplandb"></a>
### Vorbereitung

Für das Erstellen der Datenbank XPlanDB ist ein Datenbankwerkzeug, wie z. B. [pgAdmin](https://www.pgadmin.org) oder das Kommandozeilentool `psql` erforderlich. Weitere Informationen zur Installation sind in der [Dokumentation](https://www.postgresql.org/docs/) beschrieben.

Die folgenden Schritte müssen ausgeführt werden:

- Verbindung zum PostgreSQL-Server als Super User (Rolle *postgres*) herstellen
- Anlegen der Datenbank und der Datenbankbenutzer `DB_INIT_USER` (1) mit Berechtigungen für DDL und DCL sowie `DB_USER` (2) mit Berechtigungen für DQL und DML:
```sql
CREATE USER "$DB_INIT_USER" PASSWORD '$DB_INIT_PASSWORD';  <1>
CREATE USER "$DB_USER" PASSWORD '$DB_PASSWORD';  <2>
CREATE DATABASE "$DB_NAME" OWNER '$DB_INIT_USER';
```
- Installation der PostGIS-Erweiterung für die neu erstellte Datenbank.
   1. Dazu als Super User (*postgres*) mit der neuen Database `$DB_NAME` verbinden und folgendes SQL-Statement ausführen:
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

> **Note:** Weitere Informationen zu der Erstellung der XPlanDB im Anhang appendix_xplandb_skript.

<a id="konfiguration-xplandb-liquibase"></a>
### Aufruf von Liquibase

Die Erstellung der XPlanDB wird dann mit dem Ausführen der Liquibase-Skripte abgeschlossen.

```bash
$LIQUIBASE_HOME/liquibase
      --driver=org.postgresql.Driver \ <1>
      --classpath=/liquibase/xplan-database-scripts.jar:./org/postgresql/postgresql/42.7.3/postgresql-42.7.3.jar \ <2>
      --search-path=/liquibase/xplan-database-scripts \ <3>
      --changelog-file=changelog_xplandb.yaml \ <4>
      --url=$XPLAN_JDBC_URL \ <5>
      --username=$XPLAN_DB_INIT_USER \ <6>
      --password=$XPLAN_DB_INIT_PASSWORD \ <7>
      update \ <8>
      -Dxplan.db.user=$XPLAN_DB_USER \ <9>
      -Dxplan.srid=$XPLAN_SERVICES_DEFAULT_CRS_SRID \ <10>
      -Dxplan.defaultCrs=$XPLAN_SERVICES_DEFAULT_CRS <11>
```
**1:** JDBC-Treiber für PostgreSQL ist in Liquibase enthalten (optional)
**2:** Pfadangaben zu den gepackten Liquibase-Dateien und zum JDBC-Treiber getrennt durch `:`
**3:** Pfad zum Ordner mit den Liquibase Changelog-Dateien
**4:** Liquibase-Datei für die XPlanDB _changelog_xplandb.yaml_
**5:** JDBC URL, z.B. `jdbc:postgresql://localhost:5432/xplanbox`
**6:** Benutzername, `$DB_INIT_USER` aus [Vorbereitung](#konfiguration-xplandb)
**7:** Passwort für den Benutzer, `$DB_INIT_PASSWORD` aus [Vorbereitung](#konfiguration-xplandb)
**8:** Liquibase Kommando [Update](https://docs.liquibase.com/commands/update/update.html)
**9:** Benutzername, `$DB_USER` aus [Vorbereitung](#konfiguration-xplandb)
**10:** PostGIS SRID in dem die Daten gespeichert werden, z.B. `25832`
**11:** Standard-Koordinatenreferenzsystem in dem die Daten vorliegen, z.B. `EPSG:25832`

### Datenbankverbindungen anpassen

- Anpassen der Datenbank-Verbindungen in den XPlanDiensten und im XPlanManagerWorkspace unter Verwendung der Rolle `$DB_USER`:
  - _<DEEGREE_WORKSPACE_ROOT>/xplan-manager-workspace/jdbc/xplan.xml_
  - _<DEEGREE_WORKSPACE_ROOT>/xplan-services-wfs-workspace/jdbc/xplan.xml_
  - _<DEEGREE_WORKSPACE_ROOT>/xplan-services-wfs-syn-workspace/jdbc/xplan.xml_
  - _<DEEGREE_WORKSPACE_ROOT>/xplan-services-wms-workspace/jdbc/xplan.xml_
1. Anpassen der Datenbank-Verbindungen im XPlanValidatorWMS, wenn die persistente Datenhaltung verwendet wird (siehe konfiguration-xplanvalidatorwms)
   1. _<DEEGREE_WORKSPACE_ROOT>/xplan-webservices-validator-wms-sql-workspace/jdbc/xplan.xml_
1. Anpassen der Datenbank-Verbindungen in den XPlanDiensten und im XPlanManagerWorkspace, wenn die Bereitstellung für INSPIRE PLU erfolgen soll:
   1. _<DEEGREE_WORKSPACE_ROOT>/xplan-webservices-inspireplu-workspace/jdbc/inspireplu.xml_
   1. _<DEEGREE_WORKSPACE_ROOT>/xplan-manager-workspace/jdbc/inspireplu.xml_

### Weiterführende Informationen zur Konfiguration des Datenbankzugriffs

In den Dateien __xplan.xml__ werden die ConnectionsPools für den Zugriff auf die Datenbank konfiguriert. Diese beinhalten neben den Verbindungsdetails wie die URL, den Nutzernamen und das Passwort weitere Details, die ggf. bei einer Installation zu berücksichtigen sind. Darunter:

* `initialSize`: Die Anzahl der initialen Verbindungen, die beim Start geöffnet werden.
* `maxTotal`: Die maximale Anzahl von offenen Verbindungen, die von Pool zeitgleich verwendet werden können.
* `maxIdle`: Die maximale Anzahl der Verbindungen, die sich ungenutzt im Pool befinden können.

Da die Anzahl der zugelassenen Verbindungen des Datenbankservers begrenzt sein kann, ist es abhängig von der Installation der xPlanBox, der Anzahl der Nutzer und gegebenenfalls weiterer Faktoren sinnvoll, die vordefinierten Werte an die Installationsumgebung anzupassen.

Alternativ zur Konfiguration von ConnectionsPools für den Zugriff auf die Datenbank kann auch eine JNDI DataSource konfiguriert werden. Details hierzu befinden sich im Handbuch von [deegree webservices](https://download.deegree.org/documentation/current/html/#anchor-configuration-jdbc).

### Konfiguration über Umgebungsvariablen

Die Anwendungskomponenten der xPlanBox werten folgende Umgebungsvariablen aus:

**Beispiel für Datenbankverbindung:**
```properties
XPLAN_DB_HOSTNAME=xplan-db <1>
XPLAN_DB_PORT=5432 <2>
XPLAN_DB_NAME=xplanbox <3>
XPLAN_DB_USER=xplanbox <4>
XPLAN_DB_PASSWORD=xplanbox <5>
XPLAN_DB_INIT_USER=initxplanbox <6>
XPLAN_DB_INIT_PASSWORD=initxplanbox <7>
```
**1:** Host-Adresse der PostgreSQL Datenbank
**2:** Port-Adresse der PostgreSQL Datenbank
**3:** Name der Datenbank
**4:** Zugangsdaten für PostgreSQL, Rolle Anwendung: Benutzername
**5:** Zugangsdaten für PostgreSQL, Rolle Anwendung: Passwort
**6:** Zugangsdaten für PostgreSQL, Rolle Super User: Benutzername
**7:** Zugangsdaten für PostgreSQL, Rolle Super User: Passwort

<a id="installation-mapserver"></a>
## Installation und Konfiguration von MapServer

Die xPlanBox unterstützt für die Darstellung von Rasterdaten den MapServer WMS. Die Installation von MapServer ist in der [Dokumentation](https://mapserver.org/installation/unix.html#installation) beschrieben.

Die Konfigurationsdateien *mapserver.map*, *internal.map*, *common.txt* und *layers.txt* sind im Distributionspaket *xplan-mapserver-config-<VERSION>.zip* enthalten und müssen in das entsprechende Verzeichnis kopiert werden.

Anschließend müssen in den Dateien verwendete Variablen durch Konfigurationswerte ersetzt werden.

Die Konfiguration des XPlanWMS mit MapServer ist im Abschnitt konfiguration-xplanwms-mapserver beschrieben.

> **Note:** Der MapServer wird zusammen mit einem S3-Objektspeicher verwendet und erfordert die Einrichtung eines S3-Objektspeichers wie im Abschnitt [S3-Objektspeicher für Rasterdaten und Begleitdokumente](#s3-storage-attachments) beschrieben.

MapServer kann über den Paketmanager der Linux-Distribution installiert werden. Weitere Hinweise zur Installation sind in der [Installationsanleitung des MapServer](https://mapserver.org/installation/unix.html#installation) zu finden.

<a id="installation-mapproxy"></a>
## Installation und Konfiguration des MapProxy

Die Installation von MapProxy ist optional und erfordert zusätzlich die Installation von [Python](https://www.python.org/) in der Version 3.12 oder höher.

Weitere Informationen zur Installation sind in der [Dokumentation](https://mapproxy.github.io/mapproxy/latest/index.html) beschrieben.

Die Konfigurationsdateien *mapproxy.yaml* und *seed.yaml* sind im [Distributionspaket](#installationskomponenten) *xplan-mapproxy-config-<VERSION>.zip* enthalten und müssen in das entsprechende Konfigurationsverzeichnis von MapProxy kopiert werden. Als Speicher für den Cache kann ein [S3-Objektspeicher](#s3-storage) verwendet werden. Die Konfigurationsdateien enthalten entsprechende Platzhalter für die [Umgebungsvariablen](#installation-umgebungsvariablen).

In der [Dokumentation von MapProxy Seeding](https://mapproxy.github.io/mapproxy/latest/seed.html) ist auch die Verwendung des Skripts `seed.yaml` beschrieben, um nach einer Änderung des Datenbestands den Cache des MapProxy zu aktualisieren.

<a id="installation-ldproxy"></a>
## Installation und Konfiguration des ldproxy

Die Installation von [ldproxy](https://github.com/ldproxy/ldproxy) ist optional.

Weitere Informationen zur Installation sind in der [Dokumentation](https://docs.ldproxy.net/de/) beschrieben.

Die Konfigurationsdateien sind im [Distributionspaket](#installationskomponenten) *xplan-ldproxy-config-<VERSION>.zip* enthalten und müssen in das entsprechende Konfigurationsverzeichnis von ldproxy kopiert werden.

<a id="installation-hale-cli"></a>
## Installation und Konfiguration von HALE CLI

Für die Transformation von Plänen aus dem XPlanGML-Datenformat in das INSPIRE Planned Land Use (PLU) Format wird die Software [HALE](https://halestudio.org/) verwendet. Wird diese Funktion nicht benötigt, dann ist die Installation des HALE CLI auch nicht erforderlich.

Für die Installation muss zunächst das HALE CLI (ZIP-Datei) von der Projektseite auf GitHub [https://github.com/halestudio/hale-cli](https://github.com/halestudio/hale-cli/releases/) heruntergeladen werden. Anschließend muss die Datei auf dem Server, auf dem der XPlanManagerWeb installiert wird, entpackt werden.

Die Konfiguration von HALE für die Verwendung in den Komponenten der xPlanBox ist im Kapitel konfiguration-hale beschrieben.

<a id="installation-keycloak"></a>
## Installation und Konfiguration von Keycloak

Die Installation von [Keycloak](https://www.keycloak.org/) ist optional.

Weitere Informationen zur Installation sind in der [Dokumentation](https://www.keycloak.org/documentation) beschrieben.

Damit Keycloak als Identity Provider genutzt werden kann, muss die xPlanBox entsprechend konfiguriert sein. Dies ist im Abschnitt konfiguration-security-rest-keycloak beschrieben.

<a id="konfiguration-der-applikationsserver"></a>
## Einrichtung der Applikationsserver

Um den Betrieb der verschiedenen im Abschnitt
Systemarchitektur und Schnittstellen beschriebenen
Komponenten zu gewährleisten, ist eine Aufteilung der Komponenten auf mehrere Tomcat-Instanzen erforderlich. Im Folgenden ist beschrieben, wie eine Installation der Komponenten auf drei Tomcat-Instanzen erfolgen kann. Werden drei Tomcat-Instanzen auf einem Server betrieben, dann sollte der Server die im Kapitel empfohlene-systemkonfiguration beschriebenen Anforderungen erfüllen.

Für den Betrieb der xPlanBox sind getrennte Tomcat-Instanzen erforderlich:
der *Anwendungs-Tomcat*, *Dienste-Tomcat* und *API-Tomcat*. Im Folgenden wird die
Konfiguration der drei Tomcat-Instanzen beschrieben.

<a id="anwendungs-tomcat"></a>
### Anwendungs-Tomcat

Im *Anwendungs-Tomcat* muss folgende Konfiguration vorgenommen werden:

1. Für die Komponenten XPlanManager und XPlanValidator muss die Umgebungsvariable _XPLANBOX_CONFIG_ gesetzt werden. Das in dieser Variable gesetzte Verzeichnis muss die Konfigurationsdateien *managerConfiguration.properties*, *managerWebConfiguration.properties* und *validatorConfiguration.properties* enthalten (siehe Kapitel [Vorbereitung der Installation](#vorbereitung-der-installation) und  [Anwendungskomponenten installieren](#anwendung-installieren)).
1. Das Verzeichnis mit den deegree Workspaces ist über die Umgebungsvariable _DEEGREE_WORKSPACE_ROOT_ gesetzt (siehe Kapitel [Vorbereitung der Installation](#vorbereitung-der-installation)).
1. Die Bibliothek deegree muss über die Variable `javax.xml.transform.TransformerFactory=net.sf.saxon.TransformerFactoryImpl` konfiguriert werden.
1. Die Bibliothek JTS muss über die Variable `jts.overlay=ng` konfiguriert werden.

> **Tip:** Es wird empfohlen die Zeitzone im *Anwendungs-Tomcat* auf "Europe/Berlin" zu konfigurieren, wenn dies nicht bereits auf Ebene des Betriebssystems gesetzt ist. Andernfalls kann es beim Editieren eines Plans veränderten Datumsangaben (z. B. Herstellungsdatum) kommen. Für die Konfiguration im Tomcat muss folgende Option zusätzlich in den `CATALINA_OPTS` ergänzt werden: `-Duser.timezone=Europe/Berlin`.

Unter Linux muss im Verzeichnis _<CATALINA_HOME>/bin_ der Instanz *Anwendungs-Tomcat* ggf. eine neue Datei mit dem Namen *setenv.sh* angelegt werden.

In dieser Datei wird die Variable `CATALINA_OPTS` wie folgt erweitert:

```text
export CATALINA_OPTS='-DXPLANBOX_CONFIG=/opt/xplanbox/xplan-manager-config -DDEEGREE_WORKSPACE_ROOT=/opt/deegree -Djts.overlay=ng -Djavax.xml.transform.TransformerFactory=net.sf.saxon.TransformerFactoryImpl -Duser.timezone=Europe/Berlin'
```

Falls bereits ein Export von `CATALINA_OPTS` in dieser Datei vorhanden ist, muss die Variable `CATALINA_OPTS` erweitert werden.

<a id="dienste-tomcat"></a>
### Dienste-Tomcat

Für den Zugriff des XPlanManager auf die REST-API des XPlanWerkWMS, muss zur Authentifizierung ein API-Key eingerichtet werden.

Für die Instanz *Dienste-Tomcat* muss die Datei _<DEEGREE_WORKSPACE_ROOT>/config.apikey_ angelegt werden, in dieser wird der API-Key für die REST-Schnittstelle aller XPlanDienste eingetragen.

**Beispiel für den Inhalt der Datei config.apikey:**
```text
xplanbox
```

Der API-Key wird beim Start der XPlanDienste automatisch angelegt und ein generierter Key gesetzt. Dieser kann nachträglich angepasst werden. Weitere Informationen finden sich dazu im Handbuch von [deegree webservices](https://download.deegree.org/documentation/current/html/#%5Fsetting%5Fup%5Fthe%5Finterface).

Für den *Dienste-Tomcat* muss auch die Variable `CATALINA_OPTS` wie folgt erweitert werden:

```text
export CATALINA_OPTS='-DDEEGREE_WORKSPACE_ROOT=/opt/deegree -Djavax.xml.transform.TransformerFactory=net.sf.saxon.TransformerFactoryImpl'
```

> **Important:** Der *Dienste-Tomcat* muss mindestens über 4GB Arbeitsspeicher verfügen,
dies kann durch Setzen der Umgebungsvariable: `export JAVA_OPTS='-Xmx4096m'` erfolgen.

<a id="api-tomcat"></a>
### API-Tomcat

Für den *API-Tomcat* muss die Variable `CATALINA_OPTS` wie auch für den [*Dienste-Tomcat*](#dienste-tomcat) wie folgt erweitert werden:

```text
export CATALINA_OPTS='-DXPLANBOX_CONFIG=/opt/xplanbox/xplan-manager-config -DDEEGREE_WORKSPACE_ROOT=/opt/deegree -Djts.overlay=ng -Djavax.xml.transform.TransformerFactory=net.sf.saxon.TransformerFactoryImpl -Duser.timezone=Europe/Berlin'
```

> **Important:** Der *API-Tomcat* muss mindestens über 4GB Arbeitsspeicher verfügen,
dies kann durch Setzen der Umgebungsvariable: `export JAVA_OPTS='-Xmx4096m'` erfolgen.

### Absicherung der Tomcat-Instanzen

Wenn die xPlanBox in einer produktiven Umgebung betrieben wird, sollten die Apache Tomcat-Instanzen abgesichert werden. Dazu sind die allgemeinen Empfehlungen aus der [Dokumentation von Apache Tomcat zum Thema Sicherheit](https://tomcat.apache.org/tomcat-10.0-doc/security-howto.html) zu beachten.

<a id="anwendung-installieren"></a>
## Anwendungskomponenten installieren

<a id="konfiguration"></a>
### Konfigurationsdateien der Anwendungskomponenten

Die ZIP-Archive mit den deegree Workspaces (s. [Überblick der Installationskomponenten](#installationskomponenten)) müssen in das Verzeichnis _<DEEGREE_WORKSPACE_ROOT>_ (s. [Vorbereitung der Installation](#vorbereitung-der-installation)) entpackt werden:

* *xplan-manager-workspace.zip*
* *xplan-services-wfs-workspace.zip*
* *xplan-services-wfs-syn-workspace.zip*
* *xplan-services-wms-workspace.zip*
* *xplan-validator-workspace.zip*
* *xplan-webservices-validator-wms-workspace.zip* (siehe konfiguration-xplanvalidatorwms)
* *xplan-webservices-inspireplu-workspace.zip* (optional)

Die ZIP-Archive mit den Konfigurationen für die XPlanManager und XPlanValidator (s. [Überblick der Installationskomponenten](#installationskomponenten)) müssen in das Verzeichnis _<XPLANBOX_CONFIG>_ (s. [Vorbereitung der Installation](#vorbereitung-der-installation)) entpackt werden:

* *xplan-manager-config-default.zip*
* *xplan-validator-config.zip* (nur erforderlich, wenn ausschließlich der XPlanValidator installiert werden soll)
* *xplan-dokumente-config.zip* (optional)

<a id="web-anwendungen"></a>
### Web-Anwendungen

Die folgenden WAR-Archive (s. [Überblick der Installationskomponenten](#installationskomponenten)) müssen in das Verzeichnis _<CATALINA_HOME>/webapps_ der Tomcat-Instanz *Dienste-Tomcat* (z. B. auf Port: 8080) kopiert werden:

* *xplan-services-wfs.war* (XPlanWFS)
* *xplan-services-wfs-syn.war* (XPlanSynWFS)
* *xplan-services-wms.war* (XPlanWMS und XPlanWerkWMS)
* *xplan-webservices-inspireplu.war* (XPlanInspirePluWMS und XPlanInspirePluWFS) (optional)
* *xplan-webservices-validator-wms.war* (XPlanValidatorWMS)

Die WAR-Archive der Anwendungskomponenten XPlanManagerWeb und XPlanValidatorWeb werden über eine weitere Tomcat-Instanz *Anwendungs-Tomcat* (z. B. auf Port: 8081) bereitgestellt:

* *xplan-manager-web.war* (XPlanManagerWeb)
* *xplan-validator-web.war* (XPlanValidatorWeb)
* *xplan-webpages.war* (XPlanRessourcen)

Die WAR-Archive der REST-API werden über eine weitere Tomcat-Instanz *API-Tomcat* (z. B. auf Port: 8082) bereitgestellt:

* *xplan-manager-api.war* (XPlanManagerAPI)
* *xplan-validator-api.war* (XPlanValidatorAPI)
* *xplan-dokumente-api.war* (XPlanDokumenteAPI; optional)

> **Tip:** Da die Komponente XPlanRessourcen eine Einstiegsseite bereitstellt, bietet es sich an, diese als ROOT-Webapp der Instanz *Anwendungs-Tomcat* zu installieren. Das WAR-Archiv *xplan-webpages.war* muss dafür im Verzeichnis *ROOT* entpackt werden.

<a id="installation-webapp-properties"></a>
### Verknüpfung von Webapp und Workspace

Für die Tomcat-Instanz *Dienste-Tomcat* muss eine *webapp.properties* Datei angelegt werden.
Diese enthält die Verknüpfung zwischen der Webapp und dem Workspace.

**Beispiel für *webapps.properties* für den *Dienste-Tomcat*:**
```properties
/xplan-services-wms=xplan-services-wms-workspace
/xplan-services-wfs-syn=xplan-services-wfs-syn-workspace
/xplan-services-wfs=xplan-services-wfs-workspace
/xplan-webservices-validator-wms=xplan-webservices-validator-wms-memory-workspace <1>
/xplan-webservices-inspireplu=xplan-webservices-inspireplu-workspace
```
**1:** dieser Workspace wird als Vorgabewert konfiguriert, alternativ kann der *xplan-webservices-validator-wms-sql-workspace* verwendet werden (weitere Informationen zur Konfiguration des XPlanValidatorWMS sind im Kapitel konfiguration-xplanvalidatorwms zu finden).

Die Datei muss unter <DEEGREE_WORKSPACE_ROOT> abgelegt werden.

<a id="standalone-app"></a>
### Eigenständige Anwendung XPlanValidatorExecutor

Der XPlanValidatorExecutor kann als eigenständige Anwendung ausgeführt werden. Dazu müssen die [Umgebungsvariablen für S3, RabbitMQ und die Datenbank](#installation-umgebungsvariablen) gesetzt sein:

```text
java -jar xplan-validator-executor.jar
```

Wenn ein zusätzliches Profil zum XPlanValidator hinzugefügt werden soll, dann muss sich die Datei mit den Validierungsregeln im Java-Classpath des XPlanValidatorExecutor befinden. In dem folgenden Beispielaufruf kann eine Datei im Ordner */xplanbox/libs/* abgelegt sein:

```text
java -cp /xplanbox/libs/*:/xplanbox/xplan-validator-executor.jar org.springframework.boot.loader.launch.JarLauncher
```

> **Tip:** Auf einem Linux-Betriebssystem wird empfohlen, die Anwendung in einer `screen`-Session zu starten.

> **Note:** Die Anwendung verbindet sich mit Port 8080. Dieser wird für die Funktionalität der Anwendung nicht benötigt und dient dem Monitoring der Anwendungskomponente. Falls der Port bereits belegt ist, kann dieser über die Variable `--server.port=<NEUER_PORT>` geändert werden.

<a id="kommandozeilen-anwendung"></a>
### Kommandozeilen-Anwendung XPlanCLI

Die Kommandozeilenkomponente XPlanCLI kann an beliebiger Stelle im Dateisystem entpackt werden. Im *bin/* Verzeichnis des Kommandozeilenwerkzeugs befindet sich das Ausführungsskript.

> **Tip:** Um das Kommandozeilenwerkzeug von einem beliebigen Ort im Dateisystem aufrufen zu können, empfiehlt es sich, die Pfade in die `PATH` Variable mit aufzunehmen.

> **Important:** Je nach Kommando des Kommandozeilenwerkzeugs müssen über Umgebungsvariablen wie z. B. `DEEGREE_WORKSPACE_ROOT` der Pfad zum deegree Workspace gesetzt werden (siehe [Umgebungsvariablen](#installation-umgebungsvariablen)).

Die einzelnen Kommandos des XPlanCLI sind im Abschnitt xplanclitools-usage beschrieben.

<a id="dokumentation"></a>
### Dokumentation

Das XPlanBenutzerhandbuch und XPlanBetriebshandbuch (s. [Überblick der Installationskomponenten](#installationskomponenten)) zu den verschiedenen Komponenten der xPlanBox liegt in den Formaten HTML und PDF vor.

## XPlanRessourcen

Die Einstiegsseite der Komponente XPlanRessourcen enthält Referenzen zu
den anderen Komponenten der xPlanBox. Die Referenzen müssen ggf. an die
Umgebung der Installation angepasst werden. In der Datei *index.html*
müssen die URLs zu den XPlanDiensten modifiziert werden:

* http://localhost:8080/xplan-services-wms/services/wms?service=WMS&request=GetCapabilities
* http://localhost:8080/xplan-services-wfs-syn/services/xplansynwfs?service=WFS&request=GetCapabilities
* http://localhost:8080/xplan-services-wfs/services/wfs40?service=WFS&request=GetCapabilities
* http://localhost:8080/xplan-services-wfs/services/wfs41?service=WFS&request=GetCapabilities
* http://localhost:8080/xplan-services-wfs/services/wfs50?service=WFS&request=GetCapabilities
* http://localhost:8080/xplan-services-wfs/services/wfs51?service=WFS&request=GetCapabilities
* http://localhost:8080/xplan-services-wfs/services/wfs52?service=WFS&request=GetCapabilities
* http://localhost:8080/xplan-services-wfs/services/wfs60?service=WFS&request=GetCapabilities

Weiterhin kann es notwendig sein, die relativ angegeben Referenzen zu
den Komponenten XPlanManagerWeb und XPlanValidatorWeb
sowie dem XPlanBenutzerhandbuch und dem XPlanBetriebshandbuch anzupassen.

<a id="post-install"></a>
## Überblick der Post-Install-Schritte

Nach Abschluss der Installation sollten folgende Aktionen ausgeführt werden:

1. Absicherung der deegree REST-Schnittstelle (Ressource */config*) für die Webapps *xplan-services-wms*, *xplan-services-wfs*, *xplan-services-wfs-syn* und *xplan-webservices-inspireplu* durch einen API-Key (Datei *config.apikey* im Workspace-Verzeichnis, siehe Kapitel [Dienste-Tomcat](#dienste-tomcat)).
1. Absicherung des Zugriffs auf die deegree REST-Schnittstelle auf IP-Adressbereiche bzw. Domänen (Tomcat-Konfigurationsdatei *context.xml* innerhalb der Webapps).
1. Betrieb der Tomcat-Instanzen hinter einem Proxy z. B. Apache httpd oder nginx.
1. Prüfung der über den XPlanManagerAPI/-Web sowie XPlanValidatorAPI/-Web hochgeladenen Dateien auf Viren und Malware durch einen Proxy mit Virenscannerfunktion (z. B. [ClamAV](https://www.clamav.net/)).
1. Absicherung des Zugriffs auf den XPlanManagerWeb durch Benutzername und Kennwort (siehe Kapitel konfiguration-security-manager).
1. Absicherung der Komponente XPlanManagerAPI ebenfalls über Benutzername und Kennwort.
1. Festlegung einer Obergrenze für die maximale Dateigröße auf Netzwerkebene, um den Upload von beliebig großen Dateien zu verhindern.

> **Caution:** Der Betrieb der xPlanBox *ohne* die Umsetzung dieser Maßnahmen kann die IT-Sicherheit der Anwendung gefährden!

# Betrieb und Wartung

<a id="xplanbox-start"></a>
## xPlanBox starten

Zum Start der xPlanBox müssen die Komponenten in folgender Reihenfolge gestartet werden:

1. Start der Datenbank
2. Start von RabbitMQ
3. Start von MapServer
4. Start aller Instanzen des Tomcat-Servers
5. Start von MapProxy (optional)

<a id="xplanbox-stop"></a>
## xPlanBox stoppen

Zum Beenden der xPlanBox müssen die Komponenten in folgender Reihenfolge gestoppt werden:

1. Stop von MapProxy (optional)
2. Stop aller Instanzen des Tomcat-Servers
3. Stop von MapServer
4. Stop von RabbitMQ
5. Stop der Datenbank
