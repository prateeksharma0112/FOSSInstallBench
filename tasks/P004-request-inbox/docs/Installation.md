# Request Inbox

## 🚀 Quick Start

### Using Docker

Run the complete application in a single container with nginx and the Go API:

```bash
# Using Docker Compose
docker-compose up -d

# Or pull from Docker Hub
docker pull jesusnoseq/request-inbox:latest
docker run -d -p 80:80 -p 8080:8080 -v inbox-data:/app/data jesusnoseq/request-inbox:latest

# Or pull from GitHub Container Registry
docker pull ghcr.io/jesusnoseq/request-inbox:latest
docker run -d -p 80:80 -p 8080:8080 -v inbox-data:/app/data ghcr.io/jesusnoseq/request-inbox:latest
```

The application will be available at `http://localhost`

📖 **[Full Docker deployment guide](DOCKER.md)**

### Using Docker Compose (Development)

Run separate containers for frontend and backend development:

```bash
docker-compose -f docker-compose-dev.yml up --build
```

This will start:

- **API server** on `http://localhost:8080`
- **Frontend** on `http://localhost:3000`

### Prerequisites

- Docker and Docker Compose (for containerized deployment)
- Go 1.24+ (for local development)
- Node.js 20+ (for local development)

### Local Development

1. **Backend setup:**

```bash
cd api
make install          # Download Go dependencies
make run-api-hot      # Start with hot reloading
```

1. **Frontend setup:**

```bash
cd front
npm install           # Install dependencies
npm start            # Start development server
```

1. **View all available commands:**

```bash
make help
```

## Project Structure

```text
request-inbox/
├── .github/workflows/       # CI/CD pipelines (GitHub Actions)
├── api/                     # Backend application (Go)
│   ├── cmd/                 # Application entry points
│   ├── pkg/                 # Shared packages and business logic
│   │   ├──  handler/        # HTTP request handlers
│   │   ├──  model/          # Data models and validation
│   │   ├──  database/       # Database abstraction layer
│   │   ├──  login/          # Authentication & authorization
│   │   └──  route/          # API route definitions
│   ├── go.mod               # Go module dependencies
│   └── air.toml             # Hot reload configuration
├── front/                   # Frontend application (React + TypeScript)
│   ├── src/                 # Source code
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Application pages
│   │   ├── services/        # API client services
│   │   └── types/           # TypeScript type definitions
│   ├── public/              # Static assets
│   ├── package.json         # Node.js dependencies
│   └── tsconfig.json        # TypeScript configuration
├── deploy/                  # Infrastructure as Code (Terraform)
│   ├── back.tf              # Backend infrastructure
│   ├── front.tf             # Frontend infrastructure
│   ├── cert.tf              # SSL certificates
│   └── variables.tf         # Configuration variables
├── docs/                    # Documentation
│   └── openapi.yaml         # API specification (OpenAPI 3.1)
├── docker-compose-local.yml # Local development environment
├── Dockerfile-api           # Backend container definition
├── Dockerfile-front         # Frontend container definition
├── Makefile                 # Development commands
└── README.md                # This file
```

### Base URLs

- **Production**: `https://api.request-inbox.com/api/v1`
- **Local Development**: `http://localhost:8080/api/v1`


## 🛠️ Development

### Available Make Commands

```bash
make help               # Show all commands
```

### Environment Variables

For local development, create `.env.development` in the `api/` directory:

```bash
# Database
DB_ENGINE=embedded

# Server
API_HTTP_PORT=8080
API_MODE=server

# CORS
CORS_ALLOW_ORIGINS=http://localhost:3000

# Authentication (optional for local development)
LOGIN_GITHUB_CLIENT_ID=your_github_client_id
LOGIN_GITHUB_CLIENT_SECRET=your_github_client_secret
LOGIN_GOOGLE_CLIENT_ID=your_google_client_id
LOGIN_GOOGLE_CLIENT_SECRET=your_google_client_secret
JWT_SECRET=your_jwt_secret
```
