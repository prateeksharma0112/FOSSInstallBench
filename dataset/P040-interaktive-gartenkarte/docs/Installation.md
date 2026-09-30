# Installation

## Voraussetzungen

| Software | Mindestversion |
|---|---|
| PHP | 8.2 |
| Composer | 2 |
| Node.js | 22 |
| npm | aktuell |

Benötigte PHP-Extensions (bei den meisten Distributionen standardmäßig aktiv):

- `ext-sqlite3` (oder den Treiber der gewählten Datenbank)
- `ext-mbstring`
- `ext-xml`
- `ext-curl`
- `ext-fileinfo`

Prüfbar mit `php -m`. Unter Ubuntu/Debian z. B.: `sudo apt install php8.2-sqlite3 php8.2-mbstring php8.2-xml php8.2-curl`.

---

## Lokales Dev-Setup

```bash
# 1. Repository klonen
git clone https://gitlab.opencode.de/wuerzburg/heimatforum/mitmachgarten.git
cd mitmachgarten

# 2. PHP-Abhängigkeiten installieren
composer install

# 3. Umgebungsdatei anlegen und App-Key generieren
cp .env.example .env
php artisan key:generate

# 4. Datenbank anlegen (SQLite, Standard-Konfiguration von Laravel)
mkdir -p database && touch database/database.sqlite
php artisan migrate

# 5. JS-Abhängigkeiten installieren
npm install

# 6. Alles starten (Backend, Queue, Logs, Vite)
composer dev
```

Die Anwendung ist dann unter http://localhost:8000 erreichbar.
Frontend-Assets werden von Vite (http://localhost:5173) bereitgestellt und automatisch eingebunden.

> **Alternativ** können Backend und Frontend auch einzeln in separaten Terminals gestartet werden:
> ```bash
> php artisan serve   # Terminal 1
> npm run dev         # Terminal 2
> ```

Sensordaten werden live von [opendata.wuerzburg.de](https://opendata.wuerzburg.de) geladen – eine Internetverbindung ist erforderlich. Es gibt keine lokalen Demo-Daten; alle Messwerte kommen direkt von der öffentlichen API.

### Alternative: Laravel Herd oder Valet

Wer [Laravel Herd](https://herd.laravel.com) oder Valet verwendet, überspringt `php artisan serve` – der PHP-Server wird von Herd/Valet übernommen.

```bash
# Projekt in Herd verlinken und PHP-Version setzen
herd link interaktive-gartenkarte
herd isolate 8.2 --site=interaktive-gartenkarte   # oder höher (8.3, 8.4)
```

Wichtig: `APP_URL` in der `.env` muss auf die lokale Domain gesetzt werden, z. B.:

```
APP_URL=http://interaktive-gartenkarte.test
```

Der Vite-Dev-Server (`npm run dev`) wird weiterhin separat benötigt.

---

## Produktions-Deployment (ohne Docker)

```bash
# Abhängigkeiten (ohne Dev-Pakete)
composer install --no-dev --optimize-autoloader

# Frontend bauen
npm ci && npm run build

# Umgebung konfigurieren
cp .env.example .env
# .env anpassen: APP_ENV=production, APP_DEBUG=false, APP_KEY=..., DB_*

php artisan key:generate
php artisan migrate --force

# Caches aufbauen
php artisan config:cache
php artisan route:cache
php artisan view:cache
```

Webserver-Konfiguration: Document Root auf `public/` zeigen lassen. Beispielkonfigurationen für nginx und Apache sind in der [Laravel-Dokumentation](https://laravel.com/docs/deployment) zu finden.

---

## Umgebungsvariablen

Alle Konfigurationsoptionen werden über die `.env`-Datei gesetzt. Vollständige Beschreibung: [docs/CONFIGURATION.md – Umgebungsvariablen](docs/CONFIGURATION.md#umgebungsvariablen).
