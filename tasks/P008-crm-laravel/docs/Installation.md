# Liberu CRM

## Installation

### Prerequisites

- PHP 8.5 or higher
- Composer
- Node.js & npm
- A supported database (MySQL, PostgreSQL, or SQLite)

### Option 1 — Automated Installer (Recommended)

The quickest way to get started is to run the included installer script from the terminal:

```bash
./setup.sh
```

The script will:
1. Optionally copy `.env.example` to `.env`
2. Ask you to confirm your database credentials are configured
3. Run `composer install` to install PHP dependencies
4. Generate an application key
5. Run database migrations (fresh) and seed the database
6. Execute the test suite to verify the installation
7. Clear and cache all Laravel optimisations
8. Optionally start the development server

> **Note 1:** The script will ask whether to overwrite an existing `.env` file. Answer `n` if you already have a configured `.env`.
>
> **Note 2:** The script runs database seeders — make sure this is intentional before proceeding.

#### Graphical Installer

If you prefer a point-and-click experience, a graphical installer is also available. Download and run it from the [releases page](https://github.com/liberu-crm/crm-laravel/releases) and follow the on-screen prompts — no terminal knowledge required.

### Option 2 — Manual Installation

```bash
git clone https://github.com/liberu-crm/crm-laravel.git
cd crm-laravel
composer install
cp .env.example .env
php artisan key:generate
# Edit .env with your database credentials, then:
php artisan migrate --seed
npm install && npm run build
php artisan serve
```

> **Note:** Ensure your `.env` file is correctly configured with your database connection details before running migrations.

### Option 3 — Docker Compose

The project ships with a production-ready `Dockerfile` (PHP 8.5, Alpine Linux, Laravel Octane + RoadRunner) and a `docker-compose.yml` that starts the app, MySQL 8, Redis 7, and optional Horizon/Reverb/Worker sidecars.

```bash
cp .env.example .env
# Edit .env with your secrets, then:
docker compose up -d --build
docker compose exec app php artisan migrate --seed
```

Open `http://localhost:8000` in your browser.

**Available profiles** (add with `--profile`):

| Profile | Service started |
|---|---|
| `horizon` | Laravel Horizon queue dashboard |
| `reverb` | Laravel Reverb WebSocket server |
| `worker` | Generic queue worker |
| `mail` | Mailpit local mail catcher |

Example: `docker compose --profile horizon --profile reverb up -d`

> The Dockerfile is based on [exaco/laravel-docktane](https://github.com/exaco/laravel-docktane). Configuration files (supervisord, php.ini, RoadRunner) live in `.docker/`.

#### Using Laravel Sail

Laravel Sail provides a lightweight Docker environment suitable for local development. It is pre-installed as a dev dependency.

```bash
./vendor/bin/sail up
```

Once the containers are running, open `http://localhost` in your browser. Press `Ctrl+C` to stop. See the [official Sail docs](https://laravel.com/docs/sail) for further options.

### Option 4 — Kubernetes

A full Kubernetes configuration using Kustomize overlays is provided in the `k8s/` directory.

```bash
# Set required variables and run the deployment script:
export APP_KEY="base64:your-key"
export DB_PASSWORD="your-db-password"
export DB_ROOT_PASSWORD="your-root-password"
export DOMAIN="crm.example.com"
bash k8s/deploy.sh
```

Or apply directly with `kubectl`:

```bash
# Development overlay
kubectl apply -k k8s/overlays/development

# Production overlay (3 replicas + HPA)
kubectl apply -k k8s/overlays/production
```

The manifests are compatible with the [Liberu Control Panel](https://github.com/liberu-control-panel/control-panel-laravel) system. They include a Deployment, Horizon worker, MySQL StatefulSet, Redis Deployment, Ingress with TLS, NetworkPolicy, ResourceQuota, and a HorizontalPodAutoscaler for production.

> **Note:** Replace placeholder values in `k8s/base/secret.yaml` with real secrets before deploying to production. Use an external secret manager (Sealed Secrets, External Secrets Operator, etc.) for production workloads.
