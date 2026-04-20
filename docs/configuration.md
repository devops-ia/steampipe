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

### Azure plugin

Create `azure.spc`:

```hcl
connection "azure" {
  plugin          = "azure"
  subscription_id = "00000000-0000-0000-0000-000000000000"
  tenant_id       = "00000000-0000-0000-0000-000000000000"
  client_id       = "00000000-0000-0000-0000-000000000000"
  client_secret   = "your-client-secret"
}
```

```bash
docker run -d --name steampipe \
  -p 9193:9193 \
  -v "$PWD/azure.spc:/home/steampipe/.steampipe/config/azure.spc:ro" \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network

docker exec steampipe steampipe plugin install azure
```

Alternatively, use environment variables instead of hardcoding credentials in the `.spc` file:

```bash
docker run -d --name steampipe \
  -p 9193:9193 \
  -v "$PWD/azure.spc:/home/steampipe/.steampipe/config/azure.spc:ro" \
  -e AZURE_SUBSCRIPTION_ID=00000000-0000-0000-0000-000000000000 \
  -e AZURE_TENANT_ID=00000000-0000-0000-0000-000000000000 \
  -e AZURE_CLIENT_ID=00000000-0000-0000-0000-000000000000 \
  -e AZURE_CLIENT_SECRET=your-client-secret \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network
```

### Kubernetes plugin

Query in-cluster resources using the default service account (when running inside Kubernetes):

```hcl
connection "kubernetes" {
  plugin = "kubernetes"
}
```

Query an external cluster using a kubeconfig file:

```bash
docker run -d --name steampipe \
  -p 9193:9193 \
  -v "$HOME/.kube:/home/steampipe/.kube:ro" \
  -v "$PWD/kubernetes.spc:/home/steampipe/.steampipe/config/kubernetes.spc:ro" \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network

docker exec steampipe steampipe plugin install kubernetes
```

With explicit context:

```hcl
connection "kubernetes" {
  plugin      = "kubernetes"
  config_path = "~/.kube/config"
  config_context = "my-context"
}
```

### GitHub plugin

```hcl
connection "github" {
  plugin = "github"
  token  = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

```bash
docker run -d --name steampipe \
  -p 9193:9193 \
  -v "$PWD/github.spc:/home/steampipe/.steampipe/config/github.spc:ro" \
  -e GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network

docker exec steampipe steampipe plugin install github
```

### Multiple connections (aggregator)

```hcl
connection "aws_dev" {
  plugin  = "aws"
  regions = ["us-east-1"]
  profile = "dev"
}

connection "aws_staging" {
  plugin  = "aws"
  regions = ["us-east-1", "eu-west-1"]
  profile = "staging"
}

connection "aws_prod" {
  plugin  = "aws"
  regions = ["us-east-1", "eu-west-1", "ap-southeast-1"]
  profile = "prod"
}

# Aggregator combines all accounts into a single queryable connection
connection "aws_all" {
  plugin      = "aws"
  type        = "aggregator"
  connections = ["aws_dev", "aws_staging", "aws_prod"]
}
```

Query all accounts at once:

```bash
docker exec steampipe steampipe query \
  "select _ctx->>'connection_name' as account, name, region from aws_all.aws_s3_bucket"
```

## Plugin HCL reference

Plugin configuration files use HCL syntax (`.spc`). Common fields shared across most plugins:

| Field | Type | Description |
|-------|------|-------------|
| `plugin` | string | Plugin name (matches installed plugin) |
| `type` | string | `"aggregator"` for multi-connection rollup (optional) |
| `connections` | list | List of connection names to aggregate (aggregator only) |

Plugin-specific fields are documented at [hub.steampipe.io](https://hub.steampipe.io).

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

## Cache configuration

Steampipe caches query results to avoid redundant API calls. By default the cache is enabled with a 5-minute TTL.

```bash
# Disable cache entirely (useful for development/debugging)
docker run -d --name steampipe \
  -p 9193:9193 \
  -e STEAMPIPE_CACHE=false \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network

# Longer cache TTL for stable data (1 hour)
docker run -d --name steampipe \
  -p 9193:9193 \
  -e STEAMPIPE_CACHE=true \
  -e STEAMPIPE_CACHE_TTL=3600 \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network

# Short TTL for near-real-time data (30 seconds)
docker run -d --name steampipe \
  -p 9193:9193 \
  -e STEAMPIPE_CACHE=true \
  -e STEAMPIPE_CACHE_TTL=30 \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network
```

Clear the cache on demand (without restarting the container):

```bash
docker exec steampipe steampipe query "select steampipe_clear_cache()"
```

## Parallelism configuration

Control how many plugin API calls run concurrently:

```bash
docker run -d --name steampipe \
  -p 9193:9193 \
  -e STEAMPIPE_MAX_PARALLEL=20 \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network
```

Lowering `STEAMPIPE_MAX_PARALLEL` reduces API rate-limiting errors at the cost of query speed. Increasing it speeds up queries over large cloud accounts but may hit provider API limits.
