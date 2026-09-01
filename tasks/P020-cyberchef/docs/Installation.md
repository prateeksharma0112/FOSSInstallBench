# CyberChef

## Running Locally

You can run CyberChef with Docker (no toolchain required) or build it from source with Node.js.

### With Docker

**Prerequisites**

- [Docker](https://www.docker.com/products/docker-desktop/)
  - Docker Desktop must be open and running on your machine


#### Option 1: Build the Docker Image Yourself

1. Build the docker image
```bash
docker build --tag cyberchef --ulimit nofile=10000 .
```
2. Run the docker container
```bash
docker run -it -p 8080:8080 cyberchef
```
3. Navigate to `http://localhost:8080` in your browser

#### Option 2: Use the pre-built Docker Image

If you prefer to skip the build process, you can use the pre-built image

```bash
docker run -it -p 8080:8080 ghcr.io/gchq/cyberchef:latest
```

Just like before, navigate to `http://localhost:8080` in your browser.

This image is built and published through our [GitHub Workflows](.github/workflows/releases.yml).

### From source

If you want to develop CyberChef or run it without Docker, you can build it directly with Node.js.

**Prerequisites**

- [Node.js](https://nodejs.org/) `v24` (see [Node.js support](#nodejs-support))


> [!NOTE] 

> You can use [nvm](https://github.com/nvm-sh/nvm) to manage Node.js versions and use the current development version in [this project](./.nvmrc) to avoid conflicts with other projects on your machine.

**Setup**

```bash
git clone https://github.com/gchq/CyberChef.git
cd CyberChef
npm install
```

**Common tasks**

| Command | Description |
| --- | --- |
| `npm start` | Run the development server with live reload at `http://localhost:8080`. |
| `npm run build` | Produce a production build in the `build/prod` directory. |
| `npm test` | Run the Node.js and operation test suites. |
| `npm run testui` | Run the browser (UI) tests. |
| `npm run lint` | Check the code against the linting rules. |
| `npm run newop` | Scaffold a new operation via the interactive quickstart script. |

If you hit an out-of-memory error while building large recipes, increase Node's heap size with `npm run setheapsize`.
