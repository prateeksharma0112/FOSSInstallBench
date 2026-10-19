## Method
Followed Installation.md: the app is a static HTML/JS web application deployed to a web server's document root, with an Elasticsearch service as the data backend. Both prerequisites were installed locally in the Ubuntu 22.04 container and the app was deployed and verified with a real headless browser.

## Components installed (application container: root of the active benchmark container, /workspace holds the source repo)
- **Web server:** nginx 1.18 (doc root `/var/www/html`), configured to serve static files and execute `.php` via FastCGI. PHP 8.1 + php-fpm (socket `/run/php/php8.1-fpm.sock`) plus the `php8.1-curl` extension (required by the shipped proxy). Both daemons started manually (no systemd in container).
- **Elasticsearch:** 7.17.28 (open-source build from artifacts.elastic.co) installed at `/opt/elasticsearch-7.17.28` (symlink `/opt/es`), running as user `elastic`, single-node, `http.port: 9200`, `network.host: 127.0.0.1`, cluster name `index-data-explorer`. Config at `/opt/elasticsearch-7.17.28/config/elasticsearch.yml`. CORS enabled with `http.cors.allow-origin: http://localhost` so the default direct mode works from a browser.
- **Web app deployment (per guide):** copied `config/`, `externalPackages/`, `i18n/`, `src/`, `php/`, `examples/`, top-level HTML pages (`index.html`, `csvParse.html`, `plausibilityCheck.html`, `elasticsearchIndexAdministration.html`, `logo.png`) and an empty toplevel `data/` folder into `/var/www/html`.
- **Sample data:** indices `index_data_explorer_demo` (10 docs) and `spotify_tracks` (6 docs, mapping from `examples/spotify/data/elasticsearch_spotify_tracks.json`) created via the REST API so explorer pages have data.

## Configuration state
- Shipped defaults already match this deployment: `config/baseConfig.json` → `elasticsearchBaseUrl: http://localhost:9200`, `proxyUrl: null` (direct mode) — no change needed.
- Proxy mode also functional: `/php/dataExplorerProxy.php` forwards JSON to ES (verified: search returned 6 hits for `spotify_tracks`). Note: upstream proxy quirk — PHP `json_decode` converts empty JSON objects `{}` to `[]`, so `{"match_all":{}}`-style bodies fail in proxy mode only; real match/aggregation queries work, and the default direct mode is unaffected.

## Access points / startup commands
- Web UI: `http://localhost/` (main explorer), `http://localhost/examples/spotify/indexSpotify.html`, `http://localhost/examples/komono/index.html`, etc.
- Elasticsearch: `http://localhost:9200` (health: `green`).
- Restarts: `nginx`; `/usr/sbin/php-fpm8.1 --daemonize --fpm-config /etc/php/8.1/fpm/php-fpm.conf`; ES: `su -s /bin/bash elastic -c "ES_JAVA_OPTS='-Xms1g -Xmx1g' /opt/es/bin/elasticsearch -d -p /opt/elasticsearch-7.17.28/elasticsearch.pid"`.
- Verification assets: `/tmp/verify/` (Playwright scripts, screenshots `main_page.png`, `spotify_barchart.png`).

## Incomplete/unknown
- KOSIS example pages require KOSIS dataset import via the `bin/` CLI scripts (Node 18 installed for that) to show real data; the guide-mandated toplevel `data/` folder exists for them.
- No issues otherwise; all guide steps completed.