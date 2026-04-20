# Examples

## Query AWS resources

Install the AWS plugin and run a query:

```bash
docker exec steampipe steampipe plugin install aws

# List all S3 buckets
docker exec steampipe steampipe query \
  "select name, region, creation_date from aws_s3_bucket order by creation_date desc"

# Find public S3 buckets
docker exec steampipe steampipe query \
  "select name, region from aws_s3_bucket where bucket_policy_is_public = true"

# List EC2 instances by state
docker exec steampipe steampipe query \
  "select instance_id, instance_type, instance_state, region from aws_ec2_instance order by instance_state"
```

## Query multiple clouds

```bash
docker exec steampipe steampipe plugin install aws azure gcp

# AWS vs Azure: compare running VMs
docker exec steampipe steampipe query "
  select 'aws' as cloud, instance_id as id, instance_type as size, region
  from aws_ec2_instance where instance_state = 'running'
  union all
  select 'azure', id, size, location
  from azure_compute_virtual_machine where power_state = 'running'
  order by cloud, region
"
```

## Query Azure resources

```bash
docker exec steampipe steampipe plugin install azure

# List all Azure VMs with their power state
docker exec steampipe steampipe query \
  "select name, location, power_state, vm_id from azure_compute_virtual_machine order by location"

# Find Azure storage accounts without HTTPS enforcement
docker exec steampipe steampipe query "
  select name, resource_group, location
  from azure_storage_account
  where enable_https_traffic_only = false
"

# List AKS clusters and their Kubernetes version
docker exec steampipe steampipe query \
  "select name, resource_group, kubernetes_version, node_resource_group from azure_kubernetes_cluster"

# Find Azure Key Vaults with soft delete disabled
docker exec steampipe steampipe query "
  select name, resource_group, location
  from azure_key_vault
  where enable_soft_delete = false or enable_soft_delete is null
"
```

## Query GCP resources

```bash
docker exec steampipe steampipe plugin install gcp

# List all GCS buckets with their location and storage class
docker exec steampipe steampipe query \
  "select name, location, storage_class, created_before from gcp_storage_bucket order by created_before desc"

# Find GCE instances that are running
docker exec steampipe steampipe query "
  select name, zone, machine_type, status
  from gcp_compute_instance
  where status = 'RUNNING'
  order by zone
"

# List GKE clusters
docker exec steampipe steampipe query \
  "select name, location, current_master_version, node_count from gcp_kubernetes_cluster"

# Find GCS buckets with public access
docker exec steampipe steampipe query "
  select name, location
  from gcp_storage_bucket
  where iam_configuration ->> 'publicAccessPrevention' != 'enforced'
"
```

## Query Kubernetes resources

```bash
docker exec steampipe steampipe plugin install kubernetes

# List all pods across all namespaces
docker exec steampipe steampipe query \
  "select name, namespace, phase, node_name from kubernetes_pod order by namespace, name"

# Find pods not in Running or Succeeded state
docker exec steampipe steampipe query "
  select name, namespace, phase
  from kubernetes_pod
  where phase not in ('Running', 'Succeeded')
"

# List all deployments with their replica counts
docker exec steampipe steampipe query "
  select name, namespace, desired_replicas, ready_replicas, available_replicas
  from kubernetes_deployment
  order by namespace, name
"

# Find deployments with unavailable replicas
docker exec steampipe steampipe query "
  select name, namespace, desired_replicas, ready_replicas
  from kubernetes_deployment
  where ready_replicas < desired_replicas
"

# List all services and their types
docker exec steampipe steampipe query \
  "select name, namespace, type, cluster_ip from kubernetes_service order by namespace, name"
```

## Query GitHub resources

```bash
docker exec steampipe steampipe plugin install github

# List all repos in an organization
docker exec steampipe steampipe query \
  "select name, visibility, stargazer_count, fork_count from github_repository where full_name like 'your-org/%'"

# Find open issues assigned to you
docker exec steampipe steampipe query "
  select repository_full_name, title, html_url, created_at
  from github_issue
  where state = 'open'
  order by created_at desc
  limit 20
"

# List recent pull requests
docker exec steampipe steampipe query "
  select repository_full_name, number, title, state, author_login, created_at
  from github_pull_request
  where created_at > now() - interval '7 days'
  order by created_at desc
"
```

## Use psql for complex queries

```bash
# Connect interactively
psql -h localhost -p 9193 -U steampipe -d steampipe

# Run a file
psql -h localhost -p 9193 -U steampipe -d steampipe -f my-query.sql

# One-liner with output formatting
psql -h localhost -p 9193 -U steampipe -d steampipe \
  -c "select name, region from aws_s3_bucket" \
  --csv > buckets.csv
```

## Connect from application code

### Python

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=9193,
    dbname="steampipe",
    user="steampipe",
    password="your-password",
    sslmode="disable",
)
cur = conn.cursor()
cur.execute("SELECT name, region FROM aws_s3_bucket")
for row in cur.fetchall():
    print(row)
conn.close()
```

### Node.js

```javascript
const { Client } = require("pg");

const client = new Client({
  host: "localhost",
  port: 9193,
  database: "steampipe",
  user: "steampipe",
  password: "your-password",
  ssl: false,
});

await client.connect();
const res = await client.query("SELECT name, region FROM aws_s3_bucket");
console.log(res.rows);
await client.end();
```

### Go

```go
package main

import (
    "database/sql"
    "fmt"
    _ "github.com/lib/pq"
)

func main() {
    db, _ := sql.Open("postgres",
        "host=localhost port=9193 dbname=steampipe user=steampipe password=your-password sslmode=disable")
    defer db.Close()

    rows, _ := db.Query("SELECT name, region FROM aws_s3_bucket")
    defer rows.Close()
    for rows.Next() {
        var name, region string
        rows.Scan(&name, &region)
        fmt.Printf("%s (%s)\n", name, region)
    }
}
```

## Steampipe + Powerpipe together

Run Steampipe as the query backend and Powerpipe as the dashboard frontend:

```bash
# See examples/docker-compose-with-powerpipe.yml
docker compose -f examples/docker-compose-with-powerpipe.yml up -d

# Install AWS plugin in Steampipe
docker compose exec steampipe steampipe plugin install aws

# Install a compliance mod in Powerpipe
docker compose exec powerpipe powerpipe mod install github.com/turbot/steampipe-mod-aws-compliance

# Open the dashboard
open http://localhost:9033
```

## Export query results

```bash
# JSON
docker exec steampipe steampipe query \
  "select * from aws_s3_bucket" --output json > buckets.json

# CSV
docker exec steampipe steampipe query \
  "select * from aws_s3_bucket" --output csv > buckets.csv

# Markdown table
docker exec steampipe steampipe query \
  "select name, region from aws_s3_bucket limit 10" --output table
```

## Security audit example

```sql
-- Find IAM users with console access and no MFA
SELECT
  user_name,
  create_date,
  password_last_used
FROM aws_iam_user
WHERE
  password_enabled = true
  AND mfa_enabled = false
ORDER BY create_date;

-- Find security groups with unrestricted inbound access
SELECT
  group_id,
  group_name,
  description,
  region
FROM aws_vpc_security_group
WHERE
  EXISTS (
    SELECT 1
    FROM jsonb_array_elements(ip_permissions) AS p
    WHERE p->>'IpRanges' LIKE '%0.0.0.0/0%'
  )
ORDER BY region, group_name;
```

## Cross-cloud compliance checks

Find unencrypted storage across AWS, Azure, and GCP:

```sql
-- AWS S3 buckets without server-side encryption
SELECT 'aws_s3' AS service, name AS resource, region
FROM aws_s3_bucket
WHERE server_side_encryption_configuration IS NULL

UNION ALL

-- Azure storage accounts without encryption in transit
SELECT 'azure_storage', name, location
FROM azure_storage_account
WHERE enable_https_traffic_only = false

ORDER BY service, resource;
```

Find public-facing resources:

```sql
-- AWS EC2 instances with public IPs
SELECT 'aws_ec2' AS service, instance_id AS id, public_ip_address AS public_ip, region
FROM aws_ec2_instance
WHERE public_ip_address IS NOT NULL

UNION ALL

-- GCP compute instances with external IPs
SELECT 'gcp_compute', name, network_interfaces::text, zone
FROM gcp_compute_instance
WHERE network_interfaces::text LIKE '%accessConfigs%natIP%'

ORDER BY service;
```

## Scheduled queries with cron

Run automated compliance reports using cron + Docker:

```bash
# Save this as check-public-buckets.sh
#!/bin/bash
docker exec steampipe steampipe query \
  "select name, region from aws_s3_bucket where bucket_policy_is_public = true" \
  --output csv > /reports/public-buckets-$(date +%Y%m%d).csv

# Add to crontab (run daily at 6am)
# 0 6 * * * /scripts/check-public-buckets.sh
```

Using Docker directly as a cron job:

```bash
# One-shot query container (exits after query completes)
docker run --rm \
  -v "$HOME/.aws:/home/steampipe/.aws:ro" \
  -v "$PWD/aws.spc:/home/steampipe/.steampipe/config/aws.spc:ro" \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe query "select name, region from aws_s3_bucket" --output json
```
