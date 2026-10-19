OpenProject was installed using the documented **Docker all-in-one** method (single container).

**Environment**: Host at `/workspace` (the OpenProject repo checkout), x86_64, Docker Engine 29.7.2 present, ~7.6GiB RAM, ample disk, Docker Hub reachable.

**Actions performed**:
1. Generated `SECRET_KEY_BASE` via `openssl rand -hex 64`, stored at `/workspace/openproject-install/secret_key_base.txt` (chmod 600).
2. Created host persistence dirs: `/var/lib/openproject/pgdata` and `/var/lib/openproject/assets`.
3. Pulled the image: `docker pull openproject/openproject:17` (digest sha256:3603f071443e16f773ca0e6bbe7f12f66eeeb95cca4540c4f93ec504305a0596).
4. Started the container (following the guide's production one-liner with data persistence):
   ```
   docker run -d -p 8080:80 --name openproject \
     -e OPENPROJECT_HOST__NAME=localhost:8080 \
     -e OPENPROJECT_HTTPS=false \
     -e OPENPROJECT_DEFAULT__LANGUAGE=en \
     -e SECRET_KEY_BASE=<generated> \
     -v /var/lib/openproject/pgdata:/var/openproject/pgdata \
     -v /var/lib/openproject/assets:/var/openproject/assets \
     openproject/openproject:17
   ```

**Resulting state**:
- Container `openproject` is **Up** and stable, running `openproject/openproject:17` (all-in-one: internal PostgreSQL 17, memcached, Apache, Rails/Puma web + GoodJob workers + hocuspocus).
- First launch initialized and seeded the DB (locale `en`), printing the guide's expected message: *"On first installation, the default admin credentials are login: admin, password: admin"*.
- Data persists at `/var/lib/openproject/pgdata` (80M, valid PostgreSQL 17 cluster) and `/var/lib/openproject/assets`.

**Access point**: **http://localhost:8080** (host 8080 → container 80). Default credentials: `admin` / `admin`.

**Startup/stop commands**: `docker stop openproject` / `docker start openproject`.

**Notes**: The image tag `17` is a floating tag (current patch resolves to the latest 17.x). Per the guide's recommendation for production one would pin a non-floating tag, but `17` is exactly what the provided guide's commands specify, so it was used as documented. No other installation method was needed; the documented method succeeded.