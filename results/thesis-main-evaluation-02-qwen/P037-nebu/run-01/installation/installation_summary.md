## Method
Followed `Installation.md` in the repo already checked out at `/workspace` (repo root, not a separate clone): `make setup` → `docker compose up` (the documented `make dev` runs `docker compose up`; used `docker compose up -d` for non-interactive operation) → `/etc/hosts` entry → Bootstrap Wizard → Matrix client SSO test. All commands run as root in the active benchmark container (Ubuntu 22.04, Docker Engine 29.7.2 + Compose plugin v5.5.0).

## Actions performed
1. **Prereq**: `make` was missing; installed via `apt-get install make`.
2. **`make setup`**: generated `.secrets/` (internal_secret, minio root/app credentials); printed dev Dex users.
3. **Environment workaround (Docker Hub block)**: `docker compose up` failed pulling `minio/minio:RELEASE.2025-09-07T16-13-09Z` and `minio/mc:RELEASE.2025-08-13T08-35-41Z` — registry returns 401 "pull access denied" for *all* tags of both repos (verified via authed registry API), while `postgres:16-alpine`, `dexidp/dex:v2.45.1`, `clamav/clamav:stable` pull fine. Replaced by downloading the exact pinned official binaries from GitHub releases (sha256-verified against published `.sha256sum` files) into `/workspace/.local-images/` and building local images with the identical tags (minio image: alpine + binary, `ENTRYPOINT ["minio"]`, `/data` owned by uid 1000).
4. **`docker compose up -d`**: built the Elixir `server` image (node asset stage + `mix release` in `elixir:1.20-alpine` builder) and started all services. Server ran 34 SQL migrations on startup and served on `0.0.0.0:4000` (Bandit 1.12.0). All containers healthy.
5. **`/etc/hosts`**: appended `127.0.0.1 dex` (guide step 3).
6. **Bootstrap Wizard** (guide step 4), driven non-interactively with curl against `http://localhost:8080/admin`:
   - Step 1: instance name `localhost` (guide's suggested value).
   - Step 2: issuer `http://dex:5556/dex`, client ID `nebu-gateway`, client secret `nebu-dev-secret`, audience `nebu-gateway`. **Deviation from guide**: the guide lists client `nebu-admin`/`nebu-admin-secret` and a "Role Claim Name: nebu_role" field, but the shipped code registers only the `nebu-gateway` client (see `dev/dex/config.yaml` and `docker-compose.yml` ADR-022 comment) and the wizard has 3 steps (Instance, OIDC, Claim Mapping) with no role-claim field; `nebu-admin` is not registered in Dex, so the guide values could not work. Canonical values confirmed from the repo's own e2e tests (`e2e/tests/features/admin/bootstrap.spec.ts`).
   - Step 3: claim mapping (user ID `name`, display name `name`, email `email`), extra scopes `email profile groups` for both Matrix and admin (required so the Dex `groups` claim appears in the ID token; confirmed by `e2e/features/admin/bootstrap.feature` which selects `instance_admin` from groups).
   - Step "First Login": full Dex OIDC authorization-code + PKCE flow with curl, logged in as `kai@example.com` / `changeme`.
   - **Admin claim selection** (not described in the guide but part of the shipped flow): POSTed `admin_group_claim_choice={"path":"groups","value":"instance_admin"}` → 302 to `/admin/dashboard`.
7. **Matrix client connectivity** (guide step 5) via the CS API instead of a browser, using `GET /_matrix/client/v3/login/sso/redirect/oidc?redirectUrl=http://localhost:8008/capture` → Dex login → callback → `loginToken` → `POST /_matrix/client/v3/login` (`m.login.token`):
   - `alex@example.com`/`changeme` → `@alex:localhost` (long-lived access token saved in `/tmp/nebu-bootstrap/alex_token.txt`).
   - Created room `!fecb8580371b5f46:localhost` (alias `#test-room:localhost`, name "Test Room").
   - Sent message via `PUT /_matrix/client/v3/rooms/{roomId}/send/m.room.message/txn-verify-1` (guide's "test messaging"); note: send is a PUT, and room IDs must be percent-encoded (`!`→`%21`, `:`→`%3A`).
   - Second account `tom@example.com`/`changeme` → `@tom:localhost`; invited by alex, joined the room, and read alex's message back.

## Final state
- Running containers: `nebu-server-1` (healthy), `nebu-postgres-1` (healthy, localhost:5432, db/user `nebu`), `nebu-dex-1` (healthy, localhost:5556), `nebu-minio-1` (healthy, S3 API localhost:9000, console localhost:9001), `nebu-clamav-1` (healthy); `nebu-createbuckets-1` exited 0 after creating `nebu-media` bucket, `nebu-app` IAM user + `nebu-app-policy`.
- Endpoints: Matrix API + admin UI on `http://localhost:8008` / `http://localhost:8080` (same listener), plus 4000.
- `server_config` (postgres `nebu` db): `bootstrap_completed=true`, `instance_name=localhost`, `oidc_issuer=http://dex:5556/dex`, `oidc_client_id=nebu-gateway`, `oidc_audience=nebu-gateway`, `admin_group_claim=instance_admin`, `admin_group_claim_path=groups`, extra scopes `email profile groups`.
- Bootstrap is now locked: `/admin/bootstrap` and unauthenticated `/admin/dashboard` redirect to `/admin/login`; `/admin/login` renders the SSO page.
- Restart/redeploy: `cd /workspace && make dev` (or `docker compose up -d`); rebuild server with `make redeploy`.
- Notes: the guide's `docker compose logs server | grep "Nebu.Application started"` line does not appear in this build's logs; the equivalent observed start evidence is `Running Nebu.Web.Router with Bandit 1.12.0 at 0.0.0.0:4000 (http)` followed by 200s on `/health`. Local MinIO image build contexts live in `/workspace/.local-images/`. Session artifacts (cookies, tokens) are in `/tmp/nebu-bootstrap/`.