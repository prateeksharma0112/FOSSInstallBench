## Getting Started

Follow these steps to quickly run the **display-server** locally using Docker.

### 1. Clone the repository

```bash
git clone https://gitlab.opencode.de/smart-city-ulm/co-learning-spaces/display-server.git
cd display-server
```

### 2. Create the environment file

Create a .env file in the project root and configure the required variables with the settings for your setup.

```bash
cp .env.example .env
```

### 3. Start the service

Run the service using Docker Compose:

```bash
docker compose up -d
```

### 4. Verify the service

After startup, the HTML pages for a specific resource will be available at

```bash
curl http://localhost:8001/resources/{resource}
or
curl 'http://localhost:8001/resources?ids={resource_A}|{resource_B}|{resource_C}|{resource_D}'
```

### 5. View logs

```bash
docker compose logs -f
```

### 6. Stop the service

```bash
docker compose down
```

The service will now periodically fetch bookings from the configured Biletado API and provide HTML pages with upcoming reservations for all configured resources.
