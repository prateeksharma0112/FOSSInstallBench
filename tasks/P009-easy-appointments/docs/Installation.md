# Easy Appointments

## ⚡ Quick Start (Development)

Clone and run the project locally using the provided Docker Compose environment:

```bash
# Clone the repository
git clone https://github.com/alextselegidis/easyappointments.git

# Navigate into the project
cd easyappointments

# Start the Docker environment
docker compose up
````

Then open a second terminal and enter the application container:

```bash id="app-shell"
docker compose exec app bash
```

Inside the container, install dependencies:

```bash id="deps"
npm install && composer install
```

Start the development watcher:

```bash id="dev"
npm start
```

Build production assets:

```bash id="build"
npm run build
```

> Note: Works on Windows (WSL recommended), macOS, and Linux using Docker Compose.

---

## 🏗️ Installation (Production)

### Requirements

* Apache or Nginx
* PHP 8.2+
* MySQL database

### Steps

1. Create a database (or use an existing one)
2. Upload the `easyappointments` folder to your server
3. Ensure the `storage` directory is writable
4. Rename `config-sample.php` to `config.php`
5. Update configuration values
6. Open the application in your browser and follow the setup wizard

Once completed, the system is ready to use.
