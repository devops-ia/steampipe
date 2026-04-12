# Contributing

Thank you for your interest in contributing! This repo builds and publishes a community Docker image for [Steampipe](https://steampipe.io).

## Prerequisites

- Docker 20.10+
- `bash`, `jq`, `python3`, `pip`
- `helm` (optional, for chart testing)

## Build the image locally

```bash
# Build with the default Steampipe version from the Dockerfile
docker build -t steampipe:dev .

# Build with a specific version
docker build --build-arg STEAMPIPE_VERSION=2.4.1 -t steampipe:dev .
```

## Run the test suite

### Unit tests (no Docker needed)

```bash
pip install -r tests/requirements.txt
python3 -m pytest tests/ --cov=compare_snapshots --cov-report=term-missing
```

### Lint the Dockerfile

```bash
docker run --rm -i hadolint/hadolint < Dockerfile
```

### Container structure tests (requires built image)

```bash
docker run --rm \
  -v "$PWD/structure-tests.yaml:/structure-tests.yaml:ro" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gcr.io/gcp-runtimes/container-structure-test:latest \
  test --image steampipe:dev --config /structure-tests.yaml
```

### Security scan

```bash
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image --severity CRITICAL --ignore-unfixed steampipe:dev
```

## How releases work

Releases are **fully automated** — do not bump versions manually.

1. [updatecli](https://www.updatecli.io/) detects new Steampipe releases and opens a PR updating `ARG STEAMPIPE_VERSION` in the `Dockerfile`.
2. The PR CI runs all tests.
3. On merge to `main`, [semantic-release](https://semantic-release.gitbook.io/) reads conventional commits, bumps the chart version, and publishes to GHCR and Docker Hub automatically.

## Commit message format

This repo uses [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add support for multi-arch builds
fix: correct plugin directory permissions
chore: bump steampipe to 2.5.0
docs: add GCP plugin configuration example
```

| Type | When to use |
|------|------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `chore` | Maintenance (version bumps, CI tweaks) |
| `docs` | Documentation only |
| `refactor` | Code restructure without behaviour change |

## Reporting bugs

Please [open an issue](https://github.com/devops-ia/steampipe/issues/new) with:

- Steampipe image version
- Docker version (`docker --version`)
- Steps to reproduce
- Expected vs actual behaviour
- Relevant logs (`docker logs steampipe`)

## Pull requests

1. Fork the repo and create a branch: `git checkout -b feat/my-improvement`
2. Make your changes
3. Run the tests (see above)
4. Commit using Conventional Commits format
5. Open a PR against `main`
