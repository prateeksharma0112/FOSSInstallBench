# Quickstart

To develop individual services, use Docker Compose to run a service with its dependencies (see [deployment/runtimes/compose/dev/](deployment/runtimes/compose/dev/)):

```bash
cd deployment/runtimes/compose/dev
make up SCENARIO=data_store_backend
```

To run and test the full platform locally, use the Kubernetes-based reference implementation (see [deployment/runtimes/kubernetes/](deployment/runtimes/kubernetes/)):

```bash
cd deployment/runtimes/kubernetes
make local-up
```

For infrastructure requirements and full deployment instructions see [OPERATIONS.md](docs/OPERATIONS.md).
