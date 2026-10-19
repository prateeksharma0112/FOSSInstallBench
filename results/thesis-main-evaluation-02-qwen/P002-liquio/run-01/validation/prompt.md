# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** Liquio

**Description:** Liquio is an innovative GovTech platform that leverages artificial intelligence and a low-code approach to drive the digital transformation of public services. It enables rapid creation, configuration, and deployment of a wide range of IT solutions, and web and mobile applications for government agencies and local governments.

## Supplied installation guide

## Guide: Installation.md

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- [Node.js](https://nodejs.org/) (v18 or higher)
- [Git](https://git-scm.com/)
- Basic understanding of JavaScript/TypeScript and Node.js

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/liquio-opensource.git
   cd liquio-opensource
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/liquio-opensource.git
   ```

### Initial Setup

#### Docker Compose Setup

**Basic requirements**

To deploy the Liquio platform locally, ensure you have Docker and Docker Compose installed on your system. You can find the official Docker Compose installation guide [here](https://docs.docker.com/compose/). Additionally, make sure you have the necessary permissions to execute shell scripts. The included shell scripts, such as `./scripts/init.sh`, are used to generate configuration files required for the platform's operation. Docker Compose is then utilized to set up and manage the containerized environment, simplifying the deployment process.

**Access control**

The basic local deployment includes an automatically generated Central Authority certificate and user X.509 certificates in PKCS#12 format, simplifying the initial setup process. These certificates are essential for secure communication and authentication within the platform. For production deployments, you can integrate your existing Public Key Infrastructure (PKI) to replace the auto-generated certificates, ensuring compliance with organizational security policies and standards.

**Local startup**

1. Run `./scripts/init.sh` to generate configuration files from templates.
2. Run `docker compose up -d` to setup Docker Compose environment.
3. Navigate to http://localhost:8082 to enter the admin panel.
4. Use the generated key file for admin located in config/admin.p12. The default password is 'admin'.
5. Logout and navigate to http://localhost:8081 to enter the cabinet.
6. Use the generated key file for demo user located in config/demo.p12. The default password is 'demo'.
7. Use the `./scripts/generate-user.sh` to create more user key files.

**Example process**

1. To deploy an example process, let's open the admin panel via admin key.
2. Navigate to Register list page: http://localhost:8082/registry
3. Click "Import" and select "examples/register-100-100.dat". Then confirm the import. This will import the register schema for students.
4. Do the same for "examples/register-100-101.dat" and "examples/register-100-102.dat". This will import the register schemas for institutions and groups.
5. Let's navigate to Workflow list: http://localhost:8082/workflow
6. Click import, continue without skipping the validation, and select "examples/workflow-1000.bpmn" file for import. Confirm to continue.
7. You can now open the workflow configuration page and play with it: http://localhost:8082/workflow/1000
8. Let's log out and open the cabinet: http://localhost:8081. Use the demo key this time.
9. Click "Order a service" and select "Student editing".

**Running Tests**

After the environment is set up, you can run Playwright tests:

```bash
cd test

# Run tests in headless mode
npm run test

# Run tests in headed mode (see browser automation)
npm run test:headed

# Run tests with Playwright UI
npm run test:ui
```

## Kubernetes Setup

For Kubernetes development and testing:

1. Install prerequisites:
   - [minikube](https://minikube.sigs.k8s.io/docs/start/)
   - [kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl)
   - [helm](https://helm.sh/docs/intro/install/)
2. Start minikube: `minikube start`.
3. Add ingress addon: `minikube addons enable ingress`.
4. Patch ingress controller to use LoadBalancer type: `kubectl patch svc ingress-nginx-controller -n ingress-nginx -p '{"spec": {"type": "LoadBalancer"}}'`.
5. Install the Helm chart: `helm install liquio ./helm-chart -f ./helm-chart/values.yaml --create-namespace --namespace liquio`.
   > Images are pulled automatically from `ghcr.io/liquio` — no local build step required.
   > **For local development:** if you have made code changes and need to rebuild images, point your shell at minikube's Docker daemon and run the build script before installing:
   > ```bash
   > eval $(minikube docker-env)
   > ./scripts/build-images.sh --registry ghcr.io/liquio --tag 0.1.0
   > # or rebuild a single service:
   > ./scripts/build-images.sh --registry ghcr.io/liquio --tag 0.1.0 --image cabinet-api
   > ```
   > Then install with `image.pullPolicy=IfNotPresent` so Kubernetes uses the locally built images instead of pulling from the registry:
   > ```bash
   > helm install liquio ./helm-chart -f ./helm-chart/values.yaml --create-namespace --namespace liquio \
   >   --set image.pullPolicy=IfNotPresent
   > ```
6. Set default namespace: `kubectl config set-context --current --namespace=liquio`
7. Wait for the deployment to be ready: `kubectl get pods -w`.
8. Setup domain name resolution:
    8.1. Start minikube tunnel (in a separate terminal, keep it running): `minikube tunnel`
    8.2. Get the LoadBalancer ClusterIP: `CLUSTER_IP=$(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.spec.clusterIP}')`
    8.3. Add service domain names to hosts file (mapped to ClusterIP): `echo "$CLUSTER_IP admin.liquio.local admin-api.liquio.local cabinet.liquio.local cabinet-api.liquio.local id.liquio.local id-api.liquio.local" | sudo tee -a /etc/hosts`
9. Generate user keys:
    9.1. `./scripts/generate-user.sh --k8s-secret "liquio-ca-certs" --first-name "Admin" --last-name "Liquio" --serial-number "0000000001" --password "admin" --output admin.p12`
    9.2. `./scripts/generate-user.sh --k8s-secret "liquio-ca-certs" --first-name "Demo" --last-name "Liquio" --serial-number "3123456789" --password "demo" --output demo.p12`
10. Access http://admin.liquio.local from the browser.

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

**Method used:** Docker Compose local deployment per Installation.md (the Kubernetes method was not used; no cluster available in this environment).

**Execution context:** Ubuntu 22.04 container, working directory `/workspace` (repository at commit `399b8b1`), Docker 29.7.2 with Compose v5.5.0, 8 CPUs / 7.6 GB RAM.

**Steps performed:**
1. Prerequisites: Docker, Docker Compose, Git, openssl were present. `jq` (required by `scripts/init.sh`) was missing and installed via `apt-get install -y jq`. Node.js on the host was not needed — all component Dockerfiles build inside `node:24` images.
2. `./scripts/init.sh` (in `/workspace`): copied `config-templates/` to `config/`, generated `.env` (service ports, Postgres/RabbitMQ credentials), injected secrets into all service configs, generated the Central Authority (`config/certificates/ca.crt` + `ca.key`), and user keys `config/admin.p12` (password `admin`) and `config/demo.p12` (password `demo`).
3. `docker compose build --parallel`: built all 26 service images from source in `/workspace/components/*`. Total build ~55 minutes; the slowest step was `npm ci` in the admin-front stage (~32 min) due to slow network. All images tagged `workspace-<service>:latest`.
4. `docker compose up -d`: started 20 containers (all services plus postgres, rabbitmq, redis).
5. **Recovery action:** the `event` container came up `unhealthy`. Diagnosis: it started before RabbitMQ was accepting connections (compose uses `service_started`, not a health condition); the AMQP reconnect path in `components/event/src/lib/message_queue/index.ts` schedules a fresh `init()` but never resolves the original connection promise, so `useRouter()` never ran and port 7004 was never bound (process idle at 0% CPU). Fixed with `docker compose restart event` after RabbitMQ became healthy — logs then showed `server-listening-started at http://0.0.0.0:7004` and the container became healthy.

**Final state:** all 20 containers `Up (healthy)` in `/workspace` (build log at `/workspace/build.log`).
- Admin panel: http://localhost:8082 (admin.p12, password `admin`)
- Cabinet: http://localhost:8081 (demo.p12, password `demo`)
- ID front: http://localhost:8080
- APIs: 8100 (id-api), 8101 (cabinet-api), 8102 (admin-api), 8103 (register), 8104 (external-reader), 8105 (filestorage)
- Example data files for later import exist in `/workspace/examples/` (register-100-10*.dat, workflow-1000.bpmn) but were not imported; that part of the guide is a manual browser exercise.

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