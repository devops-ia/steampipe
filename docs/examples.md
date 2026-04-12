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
