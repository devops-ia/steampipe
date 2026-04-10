# steampipe

[![CI](https://github.com/devops-ia/steampipe/actions/workflows/docker-build.yml/badge.svg)](https://github.com/devops-ia/steampipe/actions/workflows/docker-build.yml)
[![GitHub release](https://img.shields.io/github/v/release/devops-ia/steampipe)](https://github.com/devops-ia/steampipe/releases)
[![Docker Hub](https://img.shields.io/docker/v/devopsiaci/steampipe?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/devopsiaci/steampipe)
[![Docker Pulls](https://img.shields.io/docker/pulls/devopsiaci/steampipe?logo=docker)](https://hub.docker.com/r/devopsiaci/steampipe)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Community Docker image for [Steampipe](https://steampipe.io) — use SQL to instantly query cloud services (AWS, Azure, GCP and more).

> **Why this image?** Turbot [stopped publishing official Docker images](https://steampipe.io/docs/managing/containers) after Steampipe v0.22.0. This project provides multi-arch container images built from official pre-compiled binaries.

## Quick start

```bash
# Run Steampipe as a service (PostgreSQL endpoint on port 9193)
docker run -d --name steampipe \
  -p 9193:9193 \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network

# Install a plugin
docker exec steampipe steampipe plugin install aws

# Connect with any PostgreSQL client
psql -h localhost -p 9193 -U steampipe -d steampipe
```

## Image details

| Property | Value |
|----------|-------|
| Base image | `debian:bookworm-slim` |
| Architectures | `linux/amd64`, `linux/arm64` |
| User | `steampipe` (UID 9193, GID 0) |
| Port | 9193 (PostgreSQL) |
| Default CMD | `steampipe service start --foreground` |

## Registries

```bash
# GitHub Container Registry
docker pull ghcr.io/devops-ia/steampipe:2.4.1

# Docker Hub
docker pull devopsiaci/steampipe:2.4.1
```

## Documentation

| Topic | Description |
|-------|-------------|
| [Getting Started](docs/getting-started.md) | Docker, Docker Compose, plugin install, first query |
| [Configuration](docs/configuration.md) | Environment variables, `.spc` plugin configs, memory tuning |
| [Kubernetes](docs/kubernetes.md) | Helm chart, OpenShift, Secrets, health checks |
| [Examples](docs/examples.md) | AWS queries, multi-cloud, Python/Node/Go clients, security audits |
| [Troubleshooting](docs/troubleshooting.md) | Connection errors, permissions, OOM, debug mode |

## Versioning

Image versions track upstream Steampipe releases 1:1. New versions are detected automatically via [updatecli](https://www.updatecli.io/) and published after merge.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).

Community Docker image for [Steampipe](https://steampipe.io) — use SQL to instantly query cloud services (AWS, Azure, GCP and more).

> **Why this image?** Turbot [stopped publishing official Docker images](https://steampipe.io/docs/managing/containers) after Steampipe v0.22.0. This project provides multi-arch container images built from official pre-compiled binaries.

## Quick start

```bash
# Run Steampipe as a service (PostgreSQL endpoint on port 9193)
docker run -d --name steampipe \
  -p 9193:9193 \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  service start --foreground --database-listen network

# Install a plugin
docker exec steampipe steampipe plugin install aws

# Connect with any PostgreSQL client
psql -h localhost -p 9193 -U steampipe -d steampipe
```

## Image details

| Property | Value |
|----------|-------|
| Base image | `debian:bookworm-slim` |
| Architectures | `linux/amd64`, `linux/arm64` |
| User | `steampipe` (UID 9193, GID 0) |
| Port | 9193 (PostgreSQL) |
| Entrypoint | `steampipe` |
| Default CMD | `service start --foreground` |

## Registries

```bash
# GitHub Container Registry
docker pull ghcr.io/devops-ia/steampipe:2.4.1

# Docker Hub
docker pull devopsiaci/steampipe:2.4.1
```

## `service start` flags

| Flag | Description | Default |
|------|-------------|---------|
| `--foreground` | Run in foreground (required for containers) | — |
| `--database-listen` | Accept connections from `local` or `network` | `local` |
| `--database-port` | PostgreSQL port | `9193` |
| `--database-password` | Set database password | random |
| `--show-password` | Show password in logs | `false` |

## Environment variables

Container-optimized defaults are pre-configured. Override as needed:

| Variable | Image default | Description |
|----------|--------------|-------------|
| `STEAMPIPE_UPDATE_CHECK` | `false` | Disable update checking |
| `STEAMPIPE_TELEMETRY` | `none` | Disable telemetry |
| `STEAMPIPE_LOG_LEVEL` | `warn` | Logging level |
| `STEAMPIPE_DATABASE_PASSWORD` | random | Database password |
| `STEAMPIPE_MEMORY_MAX_MB` | `1024` | Process memory soft limit (MB) |
| `STEAMPIPE_PLUGIN_MEMORY_MAX_MB` | `1024` | Per-plugin memory soft limit (MB) |
| `STEAMPIPE_CACHE` | `true` | Enable/disable query cache |
| `STEAMPIPE_CACHE_TTL` | `300` | Cache TTL in seconds |
| `STEAMPIPE_QUERY_TIMEOUT` | `240` | Query timeout in seconds |
| `STEAMPIPE_INSTALL_DIR` | `/home/steampipe/.steampipe` | Installation directory |
| `STEAMPIPE_DIAGNOSTIC_LEVEL` | `NONE` | Diagnostic level (`ALL`, `NONE`) |

Full reference: [Steampipe Environment Variables](https://steampipe.io/docs/reference/env-vars/overview)

## Kubernetes / Helm

This image is designed to work with the [helm-steampipe](https://github.com/devops-ia/helm-steampipe) Helm chart:

- **UID 9193 / GID 0** — compatible with OpenShift restricted SCC
- **Directory structure** matches chart volume mounts (`/home/steampipe/.steampipe/{config,internal,logs,plugins}`, `/workspace`)
- **Shell available** (`/bin/bash`, `/bin/sh`) for init container scripts

## Versioning

Image versions track upstream Steampipe releases 1:1:

| Image tag | Steampipe version |
|-----------|-------------------|
| `2.4.1` | [v2.4.1](https://github.com/turbot/steampipe/releases/tag/v2.4.1) |

New versions are detected automatically via [updatecli](https://www.updatecli.io/) and published after merge.

## License

MIT — see [LICENSE](LICENSE).