# Integrations

Steampipe exposes a standard PostgreSQL endpoint (port 9193), so it works with any tool that supports PostgreSQL connections.

## Grafana

Connect Grafana to Steampipe using the built-in PostgreSQL datasource.

### Docker Compose setup

```yaml
# docker-compose-grafana.yml
services:
  steampipe:
    image: ghcr.io/devops-ia/steampipe:v2.4.1
    container_name: steampipe
    command: steampipe service start --foreground --database-listen network
    ports:
      - "9193:9193"
    volumes:
      - steampipe-data:/home/steampipe/.steampipe
    environment:
      STEAMPIPE_DATABASE_PASSWORD: steampipe
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -h localhost -p 9193 -U steampipe"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 30s

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    depends_on:
      steampipe:
        condition: service_healthy

volumes:
  steampipe-data:
```

### Configure the datasource

In Grafana → **Connections** → **Add data source** → **PostgreSQL**:

| Field | Value |
|-------|-------|
| Host | `steampipe:9193` |
| Database | `steampipe` |
| User | `steampipe` |
| Password | your `STEAMPIPE_DATABASE_PASSWORD` value |
| TLS/SSL Mode | `disable` |

### Example dashboard query

```sql
SELECT
  NOW() AS time,
  count(*) AS value,
  instance_state AS metric
FROM aws_ec2_instance
GROUP BY instance_state
```

## Apache Superset

```yaml
# docker-compose-superset.yml
services:
  steampipe:
    image: ghcr.io/devops-ia/steampipe:v2.4.1
    command: steampipe service start --foreground --database-listen network
    ports:
      - "9193:9193"
    volumes:
      - steampipe-data:/home/steampipe/.steampipe
    environment:
      STEAMPIPE_DATABASE_PASSWORD: steampipe
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -h localhost -p 9193 -U steampipe"]
      interval: 10s
      retries: 10
      start_period: 30s

  superset:
    image: apache/superset:latest
    ports:
      - "8088:8088"
    depends_on:
      steampipe:
        condition: service_healthy

volumes:
  steampipe-data:
```

Add the database connection in Superset with this SQLAlchemy URI:

```
postgresql+psycopg2://steampipe:steampipe@steampipe:9193/steampipe
```

## Metabase

```yaml
# docker-compose-metabase.yml
services:
  steampipe:
    image: ghcr.io/devops-ia/steampipe:v2.4.1
    command: steampipe service start --foreground --database-listen network
    ports:
      - "9193:9193"
    volumes:
      - steampipe-data:/home/steampipe/.steampipe
    environment:
      STEAMPIPE_DATABASE_PASSWORD: steampipe
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -h localhost -p 9193 -U steampipe"]
      interval: 10s
      retries: 10
      start_period: 30s

  metabase:
    image: metabase/metabase:latest
    ports:
      - "3000:3000"
    depends_on:
      steampipe:
        condition: service_healthy

volumes:
  steampipe-data:
```

In Metabase → **Admin** → **Databases** → **Add database**:

| Field | Value |
|-------|-------|
| Database type | PostgreSQL |
| Host | `steampipe` |
| Port | `9193` |
| Database name | `steampipe` |
| Username | `steampipe` |
| Password | your `STEAMPIPE_DATABASE_PASSWORD` value |

## dbt

Use dbt to build models on top of Steampipe's live cloud data.

### profiles.yml

```yaml
# ~/.dbt/profiles.yml
steampipe:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      port: 9193
      dbname: steampipe
      user: steampipe
      password: steampipe
      schema: public
      sslmode: disable
```

### Example dbt model

```sql
-- models/aws_public_buckets.sql
{{ config(materialized='view') }}

SELECT
  name,
  region,
  creation_date
FROM {{ source('steampipe', 'aws_s3_bucket') }}
WHERE bucket_policy_is_public = true
```

### Run dbt against Steampipe

```bash
# Start Steampipe
docker run -d --name steampipe \
  -p 9193:9193 \
  -v steampipe-data:/home/steampipe/.steampipe \
  -e STEAMPIPE_DATABASE_PASSWORD=steampipe \
  ghcr.io/devops-ia/steampipe:v2.4.1 \
  steampipe service start --foreground --database-listen network

# Run dbt
dbt run --profiles-dir ~/.dbt --project-dir ./my-dbt-project
```

## psql

Connect with the standard `psql` CLI:

```bash
# Interactive session
psql -h localhost -p 9193 -U steampipe -d steampipe

# One-liner query
psql -h localhost -p 9193 -U steampipe -d steampipe \
  -c "SELECT name, region FROM aws_s3_bucket WHERE bucket_policy_is_public = true"

# Export to CSV
psql -h localhost -p 9193 -U steampipe -d steampipe \
  -c "COPY (SELECT name, region FROM aws_s3_bucket) TO STDOUT CSV HEADER" \
  > buckets.csv

# Run a SQL file
psql -h localhost -p 9193 -U steampipe -d steampipe -f audit.sql
```

## Python (psycopg2)

```python
import psycopg2
import csv

conn = psycopg2.connect(
    host="localhost",
    port=9193,
    dbname="steampipe",
    user="steampipe",
    password="your-password",
    sslmode="disable",
)
cur = conn.cursor()

# Query AWS resources
cur.execute("SELECT name, region, creation_date FROM aws_s3_bucket ORDER BY creation_date DESC")
for row in cur.fetchall():
    print(row)

conn.close()
```

## Node.js (pg)

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

// Query EC2 instances
const res = await client.query(
  "SELECT instance_id, instance_type, instance_state, region FROM aws_ec2_instance WHERE instance_state = $1",
  ["running"]
);
console.log(res.rows);

await client.end();
```

## Go (lib/pq)

```go
package main

import (
    "database/sql"
    "fmt"
    "log"
    _ "github.com/lib/pq"
)

func main() {
    connStr := "host=localhost port=9193 dbname=steampipe user=steampipe password=your-password sslmode=disable"
    db, err := sql.Open("postgres", connStr)
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    rows, err := db.Query("SELECT name, region FROM aws_s3_bucket")
    if err != nil {
        log.Fatal(err)
    }
    defer rows.Close()

    for rows.Next() {
        var name, region string
        rows.Scan(&name, &region)
        fmt.Printf("Bucket: %s (%s)\n", name, region)
    }
}
```

## Steampipe + Powerpipe

Powerpipe is the companion dashboard and compliance tool for Steampipe. See [`examples/docker-compose-with-powerpipe.yml`](../examples/docker-compose-with-powerpipe.yml) for a ready-to-run setup.

```bash
docker compose -f examples/docker-compose-with-powerpipe.yml up -d

# Install AWS plugin in Steampipe
docker compose exec steampipe steampipe plugin install aws

# Install a compliance mod in Powerpipe
docker compose exec powerpipe powerpipe mod install github.com/turbot/steampipe-mod-aws-compliance

# Open dashboard at http://localhost:9033
```
