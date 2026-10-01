# Setup

## 1. Voraussetzungen

Installiere Docker Engine mit dem Compose-Plugin nach der offiziellen
[Docker-Dokumentation](https://docs.docker.com/engine/install/). Für den Betrieb
ohne dauerhaftes `sudo` kann ein dedizierter Benutzer Mitglied der Gruppe
`docker` werden:

```bash
sudo adduser deploy
sudo usermod -aG docker deploy
su - deploy
docker ps
```

## 2. Repository und Konfiguration

```bash
git clone https://gitlab.opencode.de/sh/digitalhub-sh/landesprogramm-offene-innovationen/kommunalenergie/gitlab-profile.git
cd gitlab-profile
cp .env.example .env
```

Passe mindestens Passwörter, Cookie-Validierungsschlüssel, Domain und
Let's-Encrypt-E-Mail in `.env` an. `SWAGGER_HTTP_AUTH_PASSWORD` schützt die
interaktive API-Dokumentation mit dem Benutzernamen `admin`. Erzeuge außerdem
den dauerhaft aufzubewahrenden Schlüssel für die Verschlüsselung der API-Secrets:

```bash
sed -i "s|^API_CREDENTIAL_ENCRYPTION_KEY=.*|API_CREDENTIAL_ENCRYPTION_KEY=$(openssl rand -base64 32)|" .env
```

Ein späterer Austausch dieses Schlüssels macht bestehende App-Credentials
unbrauchbar; diese müssen dann rotiert werden. Für produktive Installationen sollten
`WEB_IMAGE` und `IOTHUBSH_ADAPTER_IMAGE` auf denselben Release- oder Commit-Tag
festgelegt werden.

Falls die Container Registry eine Anmeldung verlangt:

```bash
docker login registry.opencode.de
```

## 3. Start mit Docker Compose

```bash
docker compose pull
docker compose up -d
docker compose ps
```

Beim ersten Start initialisiert PostgreSQL das Basisschema automatisch. Danach
führt der Webcontainer alle ausstehenden Yii-Migrationen aus und startet Apache
erst nach deren erfolgreichem Abschluss.

Die Startprotokolle können wie folgt verfolgt werden:

```bash
docker compose logs -f web postgres
```

## 4. Erreichbarkeit

Das Webinterface ist unter der in `APP_DOMAIN` angegebenen Domain erreichbar.
Die Administration befindet sich unter `https://APP_DOMAIN/administration`.
Das initiale Administrationskonto heißt `admin`; sein Kennwort wird nur bei der
Erstellung eines leeren Datenbank-Volumes aus `INITIAL_ADMIN_PASSWORD` gelesen.
Die Swagger UI unter `https://APP_DOMAIN/administration/docs/` verwendet ebenfalls
den Benutzernamen `admin`, aber das bei jedem Containerstart neu eingelesene
`SWAGGER_HTTP_AUTH_PASSWORD`.

Der Endpunkt zur Erfassung von Messdaten liegt unter
`https://APP_DOMAIN/api/v1/node/measurements`. Weitere Angaben stehen im Ordner
`docs/`.

## Updates

```bash
docker compose pull
docker compose up -d --remove-orphans
docker compose logs -f web
```

Auch bei Updates werden Migrationen automatisch vor dem Webserver ausgeführt.
Für reproduzierbare Rollbacks sollte in `.env` ein unveränderlicher Release-
oder Commit-Tag statt `latest` verwendet werden.

## Lokale Images bauen

Für Entwicklung oder Tests können beide Images aus dem Checkout gebaut werden:

```bash
docker compose -f docker-compose.yml -f docker-compose.build.yml up -d --build
```

## Datenbank sichern und wiederherstellen

```bash
docker compose exec -T postgres pg_dump -U yii2_user yii2_db > backup.sql
docker compose exec -T postgres psql -U yii2_user -d yii2_db -v ON_ERROR_STOP=1 < backup.sql
```

Passe Benutzer und Datenbanknamen an die Werte aus `.env` an.
