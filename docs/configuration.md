# Configuration

## Environment variables

All container-optimized defaults are pre-configured. Override any variable with `-e KEY=value` or in your Compose file.

| Variable | Image default | Description |
|----------|--------------|-------------|
| `STEAMPIPE_UPDATE_CHECK` | `false` | Disable automatic update checks |
| `STEAMPIPE_TELEMETRY` | `none` | Disable telemetry (`none` or `info`) |
| `STEAMPIPE_LOG_LEVEL` | `warn` | Log verbosity (`trace`, `debug`, `info`, `warn`, `error`) |
| `STEAMPIPE_DATABASE_PASSWORD` | random | PostgreSQL password for the `steampipe` user |
| `STEAMPIPE_DATABASE_PORT` | `9193` | PostgreSQL port |
| `STEAMPIPE_MEMORY_MAX_MB` | `1024` | Soft memory limit for the Steampipe process |
| `STEAMPIPE_PLUGIN_MEMORY_MAX_MB` | `1024` | Soft memory limit per plugin |
| `STEAMPIPE_CACHE` | `true` | Enable/disable query result cache |
| `STEAMPIPE_CACHE_TTL` | `300` | Cache TTL in seconds |
| `STEAMPIPE_QUERY_TIMEOUT` | `240` | Query timeout in seconds |
| `STEAMPIPE_MAX_PARALLEL` | `10` | Maximum parallel query executions |
| `STEAMPIPE_INSTALL_DIR` | `/home/steampipe/.steampipe` | Steampipe home directory |
| `STEAMPIPE_DIAGNOSTIC_LEVEL` | `NONE` | Diagnostic level (`ALL` or `NONE`) |

Full reference: [Steampipe Environment Variables](https://steampipe.io/docs/reference/env-vars/overview)

## Set a fixed database password

```bash
docker run -d --name steampipe \
  -p 9193:9193 \
  -e STEAMPIPE_DATABASE_PASSWORD=supersecret \
  -e STEAMPIPE_DATABASE_LISTEN=network \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network
```

## Plugin configuration (.spc files)

Plugins are configured via HCL files (`.spc`) mounted into `/home/steampipe/.steampipe/config/`.

### AWS plugin — credentials via environment variables

Create `aws.spc`:

```hcl
connection "aws" {
  plugin  = "aws"
  regions = ["us-east-1", "eu-west-1"]
}
```

Mount it and pass credentials as environment variables:

```bash
docker run -d --name steampipe \
  -p 9193:9193 \
  -v "$PWD/aws.spc:/home/steampipe/.steampipe/config/aws.spc:ro" \
  -e AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE \
  -e AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY \
  -e AWS_DEFAULT_REGION=us-east-1 \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network
```

### AWS plugin — credentials via mounted profile

```bash
docker run -d --name steampipe \
  -p 9193:9193 \
  -v "$HOME/.aws:/home/steampipe/.aws:ro" \
  -v "$PWD/aws.spc:/home/steampipe/.steampipe/config/aws.spc:ro" \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network
```

### GCP plugin

```hcl
connection "gcp" {
  plugin  = "gcp"
  project = "my-project-id"
}
```

```bash
docker run -d --name steampipe \
  -p 9193:9193 \
  -v "$PWD/gcp.spc:/home/steampipe/.steampipe/config/gcp.spc:ro" \
  -v "$PWD/service-account.json:/home/steampipe/.config/gcloud/application_default_credentials.json:ro" \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network
```

### Multiple connections (aggregator)

```hcl
connection "aws_dev" {
  plugin  = "aws"
  regions = ["us-east-1"]
  # profile = "dev"
}

connection "aws_prod" {
  plugin  = "aws"
  regions = ["us-east-1", "eu-west-1"]
  # profile = "prod"
}

connection "aws_all" {
  plugin      = "aws"
  type        = "aggregator"
  connections = ["aws_dev", "aws_prod"]
}
```

## Kubernetes Secrets for plugin credentials

In Kubernetes, store credentials as Secrets and inject them as environment variables or mounted files. See [Kubernetes](kubernetes.md) for full examples.

## Memory tuning

For large datasets or many concurrent queries, increase the memory limits:

```bash
docker run -d --name steampipe \
  -p 9193:9193 \
  -e STEAMPIPE_MEMORY_MAX_MB=4096 \
  -e STEAMPIPE_PLUGIN_MEMORY_MAX_MB=2048 \
  -e STEAMPIPE_MAX_PARALLEL=20 \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network
```

Also set Docker memory limits to match:

```bash
docker run -d --name steampipe \
  --memory=6g --memory-swap=6g \
  -p 9193:9193 \
  -e STEAMPIPE_MEMORY_MAX_MB=4096 \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network
```
