# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** Startuphafen

**Description:** Startuphafen is a webapplication designed to help users navigate the german company application process.

## Supplied installation guide

## Guide: Installation.md

# Deployment System

Read the separate [README](tools/deploy3/README.md)

## Dev Logins (Keycloak devcontainer realm)

The local Keycloak instance imports a development realm with three seeded
users (dev environment only — never reuse these anywhere):

| Username | Password | Purpose                                             |
| -------- | -------- | --------------------------------------------------- |
| admin    | admin    | Realm admin + application admin (`startuphafen-admin`) |
| alice    | alice    | Activated standard user                              |
| marie    | marie    | Fresh user without activation (first-login flows)    |

## Dev Ports

- caddy proxy: 4000 (use for development)
- angular: 4201
- express-backend: 5000
- pg_admin: 3838
- kc-admin: 4000/kc-admin
- keycloak (direct): 28080
- maildev: 1080

## General Concepts

### tRPC

For typesafe communication between frontend and backend this project uses tRPC. TRPC Routers are imported into the **apps/startuphafen-backend/src/router.ts** and need to be manually created. Routers have a security measure by which only certain users with specified roles are allowed to access these endpoints. The roles are **anon, login, bundID-low, bundID-high** and increase in severity left to right. The roles are specified in the meta tag of the route.

```ts
 hello: shRoute
      .meta({
        requiredRolesAny: ['login'],
      })
      .output(z.string())
      .query(async () => {
        return 'Hello World';
      }),
```

The tRPC-Client service used from the frontend is located in the angular common library. To modify the middleware used by tRPC locate the trpc-root library.

### Angular

Angular components are separated by feature and split into display and container components. Most logic should be done in the container.component.ts

```
>feature_1
  >f1_container
    >f1-container.component.ts
    >f1-container.component.spec.ts
    >f1-container.component.html
  >f1_display
    >f1-display.component.ts
    >f1-display.component.spec.ts
    >f1-display.component.html
```

## External services

When setting up, external services (like strapi or eric) won't work in the dev environment without creating a config for it.

Create a file named **.localConfigs.json** at apps/startuphafen-backend/src/assets

```json
{
  "strapi": { "host": "", "token": "" },
  "eric": { "host": "", "token": "", "finanzaemter": [ { "name": "", "bufaNr": "", "jurisdiction": "" } ] },
  "ozg": {
    "host": "",
    "control": {
      "zustaendigeStelle": "",
      "leikaIds": [],
      "formId": "",
      "name": "",
      "serviceKonto": {
        "type": "",
        "trustLevel": "",
        "postfachAddress": {
          "identifier": "",
          "type": ""
        }
      }
    }
  },
  "mistral": {
    "apiKey": ""
  }
}
```

Make sure that the file is in the .gitignore!

The file will be automatically created during deploy.

The needed API-Token can be found your strapi instance and has to be created.

The MistralAI Api-Token can be created on the MistralAI website in your organization's project.

## Prisma

In this project we use Prisma for managing database migrations.
Prisma at its core is an ORM so it uses its own schema language to map database objects to their own model types.
The schema file can be found under **apps/startuphafen-backend/src/assets/prisma/schema.prisma**.

## Quickstart

To start development you need the Dev Containers Visual Studio Code Extension from microsoft. Build the devcontainer from scratch and your workspace is good to go.

To set up strapi properly reference the following zod-types in **libs/startuphafen-common/src/lib/entities.ts**. These have to be created and filled accordingly with data to make the application work.

StrapiType
ArticleCategory
ArticleIcon
Artikel
FAQItem
Faq
Contact
WebsiteText
LoginPageTexts
CatalogueQuestion as Questions
Catalogue as QuestionCatalogue

To use strapi either setup a strapi instance locally or on an external server by using the official Strapi documentation.
Strapi questions have to be setup in the Questions Collection. The QuestionCatalogue contains relations to the needed questions in order of appearance inside the application. Refer to the official ERiC documentation on their content and their requirements and ideally consult with a tax advisor.

For legal reasons we can't provide the ERiC gateway itself. It needs to be created with a valid certificate from ELSTER. Use the npm package koffi to create a mapper between JS and C to call the ERiC-library. Create an endpoint called /makeEricCall in the gateway that accepts an input of type EricHandleProcessInput (found in **libs/startuphafen-common/src/lib/entities.ts**) to make the necessary call to ERiC. Further information can be obtained from ELSTER, requirement is a Developer Account from ELSTER. Please contact ELSTER to get started on that front. We can't provide any further information on that part.

For local development with ERiC, copy the eric-gateway into the devcontainer at root or setup a docker container within the same network as the others of the devcontainer.

OZG is a standard REST API. The parameters for the url are referenced in the official OZG Documentation. The payload request needs to of type FormDataNode[] (found in **libs/startuphafen-common/src/lib/entities.ts**). Depending on your region OZG might not be viable solution, and you need to find an alternative.

Connecting directly via BundID is nearly impossible. The common approach is to use a BundID intermediary, such as OpenRathaus or Dataport. This repository already includes a preconfigured Keycloak setup in which Dataport is registered as a BundID IdentityProvider located in **apps/startuphafen-backend/src/assets/keycloak/templates/realm.json**. Note that the local keycloak instance, used in development, uses a different realm.json located in **.devcontainer/keycloak/imports/startuphafen.json**. The variable values must be replaced (at deploy time) with the correct values provided by Dataport.

To run locally use the npm scripts `front` and `back`.

### Pitfalls

- Only edit the prisma SQL migration files manually in exceptional circumstances, _know what you're doing_ if you do.

### Creating a new Database Migration

1. navigate to the schema file
2. create or edit prisma models according to their standard (https://www.prisma.io/docs/orm/prisma-schema/data-model/models)
3. create a db migration
   - run `npx prisma migrate dev --name [migration name here]` to apply the changes in the prisma schema file to the database and create a new migration from it
   - or run `npx prisma db push` to prototype your schema changes locally without creating a new migration file
   - to reset a db push migration run `npx prisma migrate reset`
4. run `npx nx run startuphafen-backend:entities` to create entitites from the newly created db entities

## Open source release notes

This repository is the open source release of the Startuphafen project. A few
things intentionally differ from the production deployment:

- **AI knowledge base ships empty.** The chatbot and the HWK pre-check
  (KI-Prüfung) require an embeddings corpus in the `VectorEmbedding` table.
  The production corpus is built from licensed third-party documents and is
  not part of this repository. Build your own corpus with
  `tools/pdf-embeddings-generator.js` and configure the source paths in
  `apps/startuphafen-backend/src/features/common/vector-store.ts`.
- **LLM system prompts are generic placeholders.** The production prompts are
  confidential. Adapt the placeholders in
  `apps/startuphafen-backend/src/features/chatbot/constants.ts` and
  `apps/startuphafen-backend/src/features/hwk-ai/constants.ts`.
- **The official HWK application form is not included.** The HWK mail feature
  fills the official "Antrag auf Eintragung" PDF of the Handwerkskammer,
  which we cannot redistribute. This repository ships a synthetic placeholder
  form with identical form field names at
  `apps/startuphafen-backend/src/assets/forms/hwk_antrag_eintragung.pdf` -
  replace it with the official form from your local Handwerkskammer.
- **The PLZ mapping contains placeholder entries only.** Fill
  `apps/startuphafen-backend/src/assets/plz-mapping/plz-mapping.json` with
  the municipalities relevant to your deployment.

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

## Startuphafen installation — SUCCESS

**Workspace:** `/workspace` (repo at commit `868cad5`, "v2.0.0 release", branch detached). Execution context: Ubuntu 22.04 host container, Docker 29.7.2, Node.js 20.20.2 installed via NodeSource.

### Method
The guide's documented path is a VS Code Dev Container built from `.devcontainer/devcontainer.json` (compose files `apps/startuphafen-backend/src/assets/docker-compose.yml` + `.devcontainer/dev-compose.yml`) with the apps run via npm scripts `front` and `back`. The documented compose references files that do not exist in the repo (`.devcontainer/keycloak/entrypoint.sh`, `.devcontainer/keycloak/themes`) and its `devcontainer` service depends on the Docker-in-Docker/VS Code desktop features. I reproduced the same architecture headlessly:

1. **Prep:** `npm install` in `/workspace` (lockfile, ~1400 pkgs); backend production build `npx nx run startuphafen-backend:build:development` → `dist/apps/startuphafen-backend`.
2. **Infra:** new compose file `/workspace/.devcontainer/dev-fixed.yml` (validated with `docker compose config`), services: `devcontainer` (image `mcr.microsoft.com/devcontainers/typescript-node:20-bookworm`, mounts `/workspace`), `caddy:2.11-alpine` (BACKEND_HOST=devcontainer:5000, FRONTEND_HOST=devcontainer:4201, port 4000), `database` (pgvector/pgvector:pg15, app/app), `keycloak-database` (postgres:15.5, kc/kc), `keycloak` (quay.io/keycloak/keycloak:26.1.2, port 28080→8180, realm import from `.devcontainer/keycloak/imports/startuphafen.json`, theme mount), `maildev` (:1080), `pgadmin` (:3838). Started with `docker compose -f .devcontainer/dev-fixed.yml up -d`.
3. **Keycloak repair:** realm import initially failed: `Caused by: org.keycloak.models.ModelException: invalidPasswordMinSpecialCharsMessage` (stack: `DefaultExportImportManager.importRealm`). KC 26 validates imported user credentials against the realm password policy; documented dev passwords (admin/alice/marie) fail `length(8) and … specialChars(1) …`. Fixed by relaxing `passwordPolicy` to `length(5)` in the dev realm JSON; import then logged `Realm 'startuphafen' imported` / `Import finished successfully`.
4. **Config:** created `apps/startuphafen-backend/src/assets/.localConfigs.json` per the guide template, adjusted to the current schema (`finanzaemter: []` instead of a string `bufaNr`/`jurisdiction` object, and omitted the `mistral` block whose empty `apiKey` throws in `MistralAIEmbeddings` and crashes startup; omitting it is schema-optional and the routers warn + degrade).
5. **Apps:** inside the `devcontainer` service, ran the documented `npm run back` (`nx run startuphafen-backend:serve:development`, watch) and `npm run front` (`nx serve startuphafen-frontend`). First frontend attempt SIGBUSed due to stale host nx caches (`.nx`, `node_modules/.cache/nx`, `.angular/cache`); after clearing and running with `NX_DAEMON=false` it compiled.

### Resulting state (all verified)
- **caddy :4000** (documented dev access point): frontend HTML 200 (title "Startuphafen"), `/styles.css` 200, `/trpc` proxied — `GET /trpc/FeatureFlags.getFeatureFlags` → 200 with 6 real DB rows, `/kc-admin` 302 (Keycloak admin console, admin/admin), `/kc` login flow with the startuphafen theme ("Anmeldung bei startuphafen").
- **backend :5000** (inside devcontainer): log `pgvector extension successfully enabled`, `All migrations have been successfully applied` (57 migrations), `[ ready ] http://0.0.0.0:5000`; root `GET /` → 200.
- **frontend :4201** (inside devcontainer): `Angular Live Development Server is listening on 0.0.0.0:4201`, `Compiled successfully`.
- **keycloak :28080** (host-published): JWKS `…/realms/startuphafen/protocol/openid-connect/certs` 200; password grant logins alice (roles `user`,`activatedUser`) and admin (admin-cli) → 200 Bearer tokens.
- **database:** 13 tables (FeatureFlag, Project, Answers, ShUser, VectorEmbedding, ChatSession, …), `_prisma_migrations`=57.
- **pgadmin :3838** 302; **maildev :1080** up (SMTP 1025 as configured; the compose healthcheck `/healthz` 404s on the v3 image, hence "unhealthy" status — cosmetic).

### Access points
- Development URL: `http://localhost:4000` (caddy); Keycloak admin `http://localhost:4000/kc-admin`; keycloak direct `:28080`; pgadmin `:3838` (pgadmin@example.com / secret); maildev `:1080`.
- Dev logins (per README): admin/admin (realm + app admin), alice/alice (activated), marie/marie (first-login flow).
- Restart: `docker compose -f /workspace/.devcontainer/dev-fixed.yml up -d`, then in `startuphafen-devcontainer`: `npm run back` and `npm run front` (or `npx nx serve startuphafen-frontend` with `NX_DAEMON=false`).

### Incomplete/out-of-scope (documented in the release notes)
No strapi/ERiC/OZG/Mistral credentials (placeholders/dev mode only); chatbot & HWK pre-check disabled without a Mistral key; ERiC gateway/ELSTER certificate, strapi content, PLZ mapping, and HWK form left as placeholders by design. The maildev healthcheck mismatch is cosmetic.

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