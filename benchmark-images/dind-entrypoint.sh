#!/bin/bash
set -euo pipefail

readonly dockerd_log=/var/log/installbench-dockerd.log
readonly readiness_timeout="${DIND_READY_TIMEOUT_SECONDS:-60}"

rm -f /var/run/docker.pid /var/run/docker.sock

# /var/lib/docker is a dedicated outer-engine volume, so overlay2 can store
# copy-on-write layers without nesting them in the sandbox's writable layer.
dockerd \
    --host=unix:///var/run/docker.sock \
    --storage-driver=overlay2 \
    >"${dockerd_log}" 2>&1 &
readonly dockerd_pid=$!

for ((attempt = 1; attempt <= readiness_timeout; attempt++)); do
    if docker info >/dev/null 2>&1; then
        exec "$@"
    fi

    if ! kill -0 "${dockerd_pid}" 2>/dev/null; then
        echo "The private Docker daemon exited before becoming ready." >&2
        cat "${dockerd_log}" >&2
        exit 1
    fi
    sleep 1
done

echo "The private Docker daemon was not ready after ${readiness_timeout} seconds." >&2
cat "${dockerd_log}" >&2
exit 1
