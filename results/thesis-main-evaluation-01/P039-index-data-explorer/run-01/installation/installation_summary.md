Installed the Index Data Explorer static web application at /workspace (git commit a8c4210).

Method: The app is static HTML/JS with all libraries vendored in externalPackages/, so no build/package install is required. Following the guide's "copy folders to the webserver document root" instructions, I served the repository toplevel directly as the nginx document root, making the required folders (config, externalPackages, i18n, src, php) and all HTML pages available.

Actions:
1. `apt-get update` then `DEBIAN_FRONTEND=noninteractive apt-get install -y python3 nginx` (nginx 1.18.0, python3 from Ubuntu 22.04 repos).
2. Wrote /etc/nginx/sites-available/daexp with `listen 8080`, `root /workspace`, `index index.html`, `try_files $uri $uri/ =404`; symlinked into sites-enabled; removed the default site.
3. Validated with `nginx -t` (success) and started nginx (master PID 1328).

Paths: repo/document root = /workspace; nginx site config = /etc/nginx/sites-available/daexp; executable = /usr/sbin/nginx.

Access point: http://localhost:8080/index.html plus example pages under /examples/.

State: nginx is running and serves all app assets. No Elasticsearch service was installed; config/baseConfig.json points at http://localhost:9200, so live data querying requires an Elasticsearch instance (and optionally php/dataExplorerProxy.php) at runtime. The optional top-level `data` folder used by some example instances already exists inside examples/*/data.