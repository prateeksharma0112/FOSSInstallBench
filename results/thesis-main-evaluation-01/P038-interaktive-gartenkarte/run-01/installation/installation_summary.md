## Method
Followed the guide's "Lokales Dev-Setup" via the alternative two-terminal approach (`php artisan serve` + `npm run dev`), since the guide documents this explicitly and the production `npm run build` path hits a repository defect (see below).

## Prerequisites installed (none existed initially)
- Added the Sury PHP repository (`/etc/apt/sources.list.d/php.list`) because Ubuntu 22.04 ships only PHP 8.1, below the required ^8.2.
- Installed **PHP 8.4.26** (`php8.4-cli` + `sqlite3, mbstring, xml, curl, gd, zip, bcmath, intl`) and set it as the default `php` alternative. PHP 8.4 was required because `composer.lock` pins several Symfony v8 packages requiring PHP >=8.4 (PHP 8.2 failed `composer install`).
- Installed **Composer 2.10.3** to `/usr/local/bin/composer`.
- Installed **Node.js 22.23.3** and **npm 10.9.9** via nodesource.

## Application setup (working dir `/workspace`)
- `composer install` — succeeded (101+ packages). Required manually creating `bootstrap/cache/` and `storage/framework/{cache/data,sessions,views}`, `storage/logs` (gitignored, absent from the checkout) before package discovery would run.
- `cp .env.example .env` and `php artisan key:generate` — succeeded.
- `touch database/database.sqlite` and `php artisan migrate` — succeeded (users, cache, jobs migrations).
- `npm install` — succeeded (286 packages).
- `npm run build` — **fails**: `Could not resolve "./UserMenuContent.vue" from NavUser.vue` (and `UserInfo.vue`); both files are absent from the repo and all upstream branches/tags.
- Started `php artisan serve --host=127.0.0.1 --port=8000` and `npm run dev --host=127.0.0.1 --port=5173` as background processes.

## Final state
- Home route `/` returns HTTP 200; HTML references Vite dev assets at :5173, which serve `app.ts`, `MainPage.vue` and its full component graph (Navigation, Sensor, Ochsi, HomeInfoCard, SensorCard, InfoCard) as HTTP 200.
- `GET /up` → 200; `GET /` → 200.
- Live API `GET /api/sensors/feldahorn/data` → 200 (32 KB HTML with real OpenData values); `GET /api/home-info-card-text` → 200.
- Access points: app http://localhost:8000, Vite http://localhost:5173.

## Incomplete / known issues
- Production build (`npm run build`) is not achievable from this commit due to the two missing Vue source files. This affects only the unused `Dashboard.vue`/`AppHeader.vue` path (no `/dashboard` route exists), not the main application route.