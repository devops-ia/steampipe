# steampipe

[![CI](https://github.com/devops-ia/steampipe/actions/workflows/docker-build.yml/badge.svg)](https://github.com/devops-ia/steampipe/actions/workflows/docker-build.yml)
[![GitHub release](https://img.shields.io/github/v/release/devops-ia/steampipe)](https://github.com/devops-ia/steampipe/releases)
[![Docker Hub](https://img.shields.io/docker/v/devopsiaci/steampipe?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/devopsiaci/steampipe)
[![Docker Pulls](https://img.shields.io/docker/pulls/devopsiaci/steampipe?logo=docker)](https://hub.docker.com/r/devopsiaci/steampipe)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Context7](https://img.shields.io/badge/Context7-docs-green)](https://context7.com/devops-ia/steampipe)

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
| [Plugins](docs/plugins.md) | Install, configure, and manage plugins (AWS, Azure, GCP, Kubernetes, GitHub, Terraform…) |
| [Integrations](docs/integrations.md) | Grafana, Superset, Metabase, dbt, Python, Node.js, Go |
| [Kubernetes](docs/kubernetes.md) | Helm chart, OpenShift, Secrets, health checks |
| [Examples](docs/examples.md) | AWS queries, multi-cloud, Python/Node/Go clients, security audits |
| [Troubleshooting](docs/troubleshooting.md) | Connection errors, permissions, OOM, debug mode |

## Versioning

Image versions track upstream Steampipe releases 1:1. New versions are detected automatically via [updatecli](https://www.updatecli.io/) and published after merge.

## Common use cases

```bash
# Security: find AWS IAM users without MFA
docker exec steampipe steampipe query "
  SELECT user_name, create_date FROM aws_iam_user
  WHERE password_enabled = true AND mfa_enabled = false"

# Cost: list unattached EBS volumes
docker exec steampipe steampipe query "
  SELECT volume_id, size, volume_type, region FROM aws_ebs_volume
  WHERE state = 'available'"

# Compliance: find Azure storage accounts without HTTPS
docker exec steampipe steampipe query "
  SELECT name, resource_group, location FROM azure_storage_account
  WHERE enable_https_traffic_only = false"

# Operations: list Kubernetes pods not running
docker exec steampipe steampipe query "
  SELECT name, namespace, phase FROM kubernetes_pod
  WHERE phase NOT IN ('Running','Succeeded')"

# Inventory: count EC2 instances by region
docker exec steampipe steampipe query "
  SELECT region, count(*) FROM aws_ec2_instance GROUP BY region ORDER BY count DESC"
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).