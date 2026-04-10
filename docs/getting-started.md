# Getting Started

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) 20.10+
- A cloud provider account (AWS, Azure, GCP, etc.) for querying

## Pull the image

```bash
# GitHub Container Registry (recommended)
docker pull ghcr.io/devops-ia/steampipe:2.4.1

# Docker Hub
docker pull devopsiaci/steampipe:2.4.1
```

## Run as a query shell

Execute a one-off interactive SQL session:

```bash
docker run -it --rm \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe query
```

## Run as a PostgreSQL service

Start Steampipe as a persistent background service accessible on port 9193:

```bash
docker run -d --name steampipe \
  -p 9193:9193 \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network
```

Verify it's running:

```bash
docker logs steampipe
# Look for: "Database is now running"
```

## Install a plugin

Plugins are installed at runtime and stored in a volume for persistence:

```bash
# Create a named volume so plugins survive container restarts
docker volume create steampipe-data

docker run -d --name steampipe \
  -p 9193:9193 \
  -v steampipe-data:/home/steampipe/.steampipe \
  -e STEAMPIPE_DATABASE_PASSWORD=mypassword \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network

# Install the AWS plugin
docker exec steampipe steampipe plugin install aws

# List installed plugins
docker exec steampipe steampipe plugin list
```

## Connect with a SQL client

Once the service is running, connect with any PostgreSQL-compatible client:

```bash
# psql
psql -h localhost -p 9193 -U steampipe -d steampipe

# DBeaver, TablePlus, DataGrip — use these connection settings:
# Host:     localhost
# Port:     9193
# Database: steampipe
# User:     steampipe
# Password: (see STEAMPIPE_DATABASE_PASSWORD or docker logs)
```

## Run with Docker Compose

See [`examples/docker-compose.yml`](../examples/docker-compose.yml) for a ready-to-use Compose setup.

```bash
cd examples
docker compose up -d
docker compose exec steampipe steampipe plugin install aws
```

## Verify the query engine works

```bash
docker exec steampipe steampipe query "select 1 as test"
# Expected output:
# +------+
# | test |
# +------+
# | 1    |
# +------+
```

## Next steps

- [Configuration](configuration.md) — env vars, plugin credentials, memory tuning
- [Examples](examples.md) — real-world queries and use cases
- [Kubernetes](kubernetes.md) — deploy with Helm
- [Troubleshooting](troubleshooting.md) — common problems and fixes
