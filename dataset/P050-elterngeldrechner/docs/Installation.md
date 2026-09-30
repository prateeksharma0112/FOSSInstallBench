# Elterngeldrechner und Planer

Elterngeldrechner mit Planer im [Familienportal des BMBFSFJ](https://familienportal.de/familienportal/meta/egr).

## Getting Started

Everything you need to get the Elterngeldrechner running locally and out to staging or production.

### Requirements

- **[mise](https://mise.jdx.dev)**: manages the development toolchain, provides the required environment variables, and exposes
  the tasks described below. Install it with `brew install mise`, then activate it in your shell (see the
  [mise docs](https://mise.jdx.dev/getting-started.html)).
- **1 Password CLI + Vault Access**: To trigger deployments from your development machine the integration between the 1password
  app and the cli must be anabled and you must have access to the **Elterngeld Engineering** vault.

### Setup

```sh
mise trust           # one-time, confirms you trust this repo's mise.toml
mise install         # installs the tools pinned in mise.toml
mise exec -- npm ci  # mise exec, so the install runs under the pinned node
hk install --global  # one-time per machine, see "Git hooks" below
```

### Development

```sh
mise run start                        # serve the widget in the host page snapshot
mise run check                        # format, type-check, lint, stylelint and test
mise run static-checks                # everything in check but the suite
mise run test-suite                   # just the vitest suite
mise run audit                        # licences, vulnerabilities and secrets
mise run link-check                   # external links in sources and documentation
```

### Git hooks

[hk](https://hk.jdx.dev) formats and lints the staged files before each commit, and validates the commit subject
against [conventional commits](https://www.conventionalcommits.org). Every step calls the same npm script as
`mise run static-checks`, so the hook cannot drift from the pipeline. See [hk.pkl](hk.pkl) for the current set.

`hk install --global` is per machine rather than per clone, so run it once, from inside this repository. Use
`hk check` to lint on demand, `hk fix` to apply the fixes and `HK=0 git commit …` to bypass the hooks.

### Secrets

Every secret a development task needs, deploying a preview or rolling production back for instance, lives in the
**Elterngeld Engineering** vault in 1Password. [fnox](https://fnox.jdx.dev) resolves it when the task runs, so no
token is written to disk. See [fnox.toml](fnox.toml), which references the secrets without holding their values.

Only secrets specific to the pipeline are CI/CD variables, such as the token for the PostHog release annotation,
scoped to that one job with minimal privileges.

### Deployment

The Elterngeldrechner can be deployed in two ways. Either just the widget, a single javascript file with the
css inlined, together with its documents and images to staging or production, or the full build including the
Familienportal wrapper as a preview in the staging bucket.

On every push to `main` the application is deployed into the staging Familienportal for integration testing. That
portal is only accessible via a virtual private network, so the same push also publishes the `main` preview, which
the team can reach without one. The production deployment happens on every release, see [Release](#release).

If you'd like to make a branch or feature flag variant of the application available for the team, please use the preview
deployment with a specified name. Please remember to delete the deployment again once unused and be aware of the usual
caveats when working on long-living branches.

If you're interested in more details on the deployment process please read
[ADR 0009](architecture-decision-records/0009-deployment-strategy-s3.md), otherwise just use one of the following
commands.

```sh
mise run deploy --preview --name <name>                     # publish a standalone page under preview/<name>/
mise run deploy --preview --name <name> --delete            # empty that preview again
mise run deploy --staging                                   # build and upload to the staging bucket root
mise run deploy --production                                # build and upload to the production bucket root
mise run deploy --production --rollback --ref <tag-or-sha>  # rebuild a past ref and publish it to production
```
