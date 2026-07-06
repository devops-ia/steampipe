# Plugins

Steampipe plugins extend the query engine to support specific cloud providers, SaaS tools, and APIs. Each plugin maps one or more external services to SQL tables.

Plugin reference: [hub.steampipe.io](https://hub.steampipe.io)

## Managing plugins

```bash
# Install a plugin
docker exec steampipe steampipe plugin install aws

# Install multiple plugins at once
docker exec steampipe steampipe plugin install aws azure gcp github kubernetes

# List installed plugins
docker exec steampipe steampipe plugin list
# Output:
# +------------+---------+-------------+
# | Name       | Version | Connections |
# +------------+---------+-------------+
# | aws        | 0.141.0 | aws         |
# | azure      | 0.63.0  | azure       |
# | gcp        | 0.54.0  | gcp         |
# | github     | 0.40.0  | github      |
# | kubernetes | 0.32.0  | kubernetes  |
# +------------+---------+-------------+

# Update a plugin to the latest version
docker exec steampipe steampipe plugin update aws

# Update all installed plugins
docker exec steampipe steampipe plugin update --all

# Uninstall a plugin
docker exec steampipe steampipe plugin uninstall aws

# Pin a specific plugin version
docker exec steampipe steampipe plugin install aws@0.140.0
```

## Plugin configuration (.spc files)

Plugins are configured via HCL files (`.spc`) placed in `/home/steampipe/.steampipe/config/`. One file can define multiple connections.

### AWS plugin

Credentials via environment variables (recommended for containers):

```hcl
# aws.spc
connection "aws" {
  plugin  = "aws"
  regions = ["us-east-1", "eu-west-1"]
}
```

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

Credentials via mounted AWS profiles:

```hcl
# aws.spc
connection "aws_dev" {
  plugin  = "aws"
  profile = "dev"
  regions = ["us-east-1"]
}

connection "aws_prod" {
  plugin  = "aws"
  profile = "prod"
  regions = ["us-east-1", "eu-west-1", "ap-southeast-1"]
}

connection "aws_all" {
  plugin      = "aws"
  type        = "aggregator"
  connections = ["aws_dev", "aws_prod"]
}
```

```bash
docker run -d --name steampipe \
  -p 9193:9193 \
  -v "$HOME/.aws:/home/steampipe/.aws:ro" \
  -v "$PWD/aws.spc:/home/steampipe/.steampipe/config/aws.spc:ro" \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network
```

### Azure plugin

Service principal authentication:

```hcl
# azure.spc
connection "azure" {
  plugin          = "azure"
  subscription_id = "00000000-0000-0000-0000-000000000000"
  tenant_id       = "00000000-0000-0000-0000-000000000000"
  client_id       = "00000000-0000-0000-0000-000000000000"
  client_secret   = "your-client-secret"
}
```

Environment variable authentication (recommended):

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

### GCP plugin

Service account authentication:

```hcl
# gcp.spc
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

### Kubernetes plugin

In-cluster (default service account):

```hcl
# kubernetes.spc
connection "kubernetes" {
  plugin = "kubernetes"
}
```

External cluster via kubeconfig:

```hcl
connection "kubernetes" {
  plugin         = "kubernetes"
  config_path    = "~/.kube/config"
  config_context = "my-cluster-context"
}
```

```bash
docker run -d --name steampipe \
  -p 9193:9193 \
  -v "$HOME/.kube:/home/steampipe/.kube:ro" \
  -v "$PWD/kubernetes.spc:/home/steampipe/.steampipe/config/kubernetes.spc:ro" \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network
```

### GitHub plugin

```hcl
# github.spc
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
```

### Terraform plugin

Query Terraform state files and plan outputs:

```hcl
# terraform.spc
connection "terraform" {
  plugin = "terraform"

  # Local state files
  configuration_file_paths = ["*.tf", "modules/**/*.tf"]
  state_file_paths         = ["terraform.tfstate", ".terraform/**/*.tfstate"]
}
```

```bash
docker run -d --name steampipe \
  -p 9193:9193 \
  -v "$PWD:/workspace" \
  -v "$PWD/terraform.spc:/home/steampipe/.steampipe/config/terraform.spc:ro" \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network
```

### Slack plugin

```hcl
# slack.spc
connection "slack" {
  plugin = "slack"
  token  = "xoxp-xxxxxxxxxxxx-xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

## Plugin persistence

Installed plugins are stored under `/home/steampipe/.steampipe/plugins/`. Use a named volume so plugins survive container recreation:

```bash
docker volume create steampipe-data

docker run -d --name steampipe \
  -p 9193:9193 \
  -v steampipe-data:/home/steampipe/.steampipe \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network

# Install plugins — they persist in steampipe-data volume
docker exec steampipe steampipe plugin install aws azure gcp
```

## Pre-installing plugins at build time

For faster cold starts, build a custom image with plugins pre-installed:

```dockerfile
FROM ghcr.io/devops-ia/steampipe:2.4.1

RUN steampipe plugin install aws azure gcp kubernetes
```

```bash
docker build -t my-steampipe .
docker run -d --name steampipe -p 9193:9193 my-steampipe \
  steampipe service start --foreground --database-listen network
```

## Discovering available tables

After installing a plugin, list the tables it provides:

```bash
# List all tables from all installed plugins
docker exec steampipe steampipe query "select * from information_schema.tables where table_schema not in ('pg_catalog', 'information_schema') order by table_schema, table_name"

# Describe a specific table's columns
docker exec steampipe steampipe query ".inspect aws_s3_bucket"
```
