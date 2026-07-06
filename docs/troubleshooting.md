# Troubleshooting

## Container exits immediately

**Symptom:** `docker run` exits right away with code 0 or 1.

**Cause:** Missing `--foreground` flag when running as a service.

```bash
# Wrong — exits after starting the background daemon
docker run ghcr.io/devops-ia/steampipe:v2.4.1 steampipe service start

# Correct — blocks in foreground (required for containers)
docker run ghcr.io/devops-ia/steampipe:v2.4.1 \
  steampipe service start --foreground --database-listen network
```

---

## Cannot connect on port 9193

**Symptom:** `psql: error: connection to server on socket failed: Connection refused`

**Cause 1:** Steampipe started without `--database-listen network` — by default it only listens on `localhost` inside the container.

```bash
# Must include --database-listen network to accept external connections
docker run -d -p 9193:9193 \
  ghcr.io/devops-ia/steampipe:v2.4.1 \
  steampipe service start --foreground --database-listen network
```

**Cause 2:** Service not yet ready — PostgreSQL bootstraps on first start (~30 seconds).

```bash
# Wait for the service to be ready
until docker exec steampipe pg_isready -h localhost -p 9193 -U steampipe; do
  echo "Waiting for Steampipe..."; sleep 5
done
```

**Cause 3:** Port not published in `docker run`.

```bash
# Publish the port explicitly
docker run -d -p 9193:9193 ...
```

---

## Plugin not found after install

**Symptom:** `Error: could not find plugin 'aws'` after `steampipe plugin install aws`.

**Cause:** Plugin was installed in a container that was later removed; no persistent volume.

```bash
# Use a named volume for the Steampipe home directory
docker volume create steampipe-data

docker run -d --name steampipe \
  -p 9193:9193 \
  -v steampipe-data:/home/steampipe/.steampipe \
  ghcr.io/devops-ia/steampipe:v2.4.1 \
  steampipe service start --foreground --database-listen network

# Plugins installed now survive container recreation
docker exec steampipe steampipe plugin install aws
```

---

## Permission denied errors

**Symptom:** `permission denied` writing to `/home/steampipe/.steampipe/` or plugin directories.

**Cause:** Volume mounted with wrong ownership; the container runs as UID 9193.

```bash
# Fix ownership on the host before mounting
sudo chown -R 9193:0 ./steampipe-data

# Or use Docker's --user flag is NOT recommended — always run as UID 9193
```

In Kubernetes, use an `initContainer` to fix permissions:

```yaml
initContainers:
  - name: fix-permissions
    image: busybox
    command: ["chown", "-R", "9193:0", "/home/steampipe/.steampipe"]
    volumeMounts:
      - name: steampipe-data
        mountPath: /home/steampipe/.steampipe
```

---

## Memory / OOM errors

**Symptom:** Container is killed with exit code 137, or queries fail with out-of-memory errors.

**Cause:** Default memory limits are conservative for large cloud accounts.

```bash
# Increase memory limits
docker run -d --name steampipe \
  --memory=4g \
  -p 9193:9193 \
  -e STEAMPIPE_MEMORY_MAX_MB=3072 \
  -e STEAMPIPE_PLUGIN_MEMORY_MAX_MB=2048 \
  ghcr.io/devops-ia/steampipe:v2.4.1 \
  steampipe service start --foreground --database-listen network
```

In Kubernetes:

```yaml
resources:
  requests:
    memory: "1Gi"
  limits:
    memory: "4Gi"
env:
  - name: STEAMPIPE_MEMORY_MAX_MB
    value: "3072"
  - name: STEAMPIPE_PLUGIN_MEMORY_MAX_MB
    value: "2048"
```

---

## Query timeout

**Symptom:** `Error: query timed out` for large queries.

```bash
# Increase timeout (default 240s)
docker exec steampipe steampipe query \
  --query-timeout 600 \
  "select * from aws_s3_bucket"

# Or set permanently via env var
docker run -e STEAMPIPE_QUERY_TIMEOUT=600 ...
```

---

## Debug mode

Enable detailed logging to diagnose unexpected behaviour:

```bash
docker run -d --name steampipe \
  -p 9193:9193 \
  -e STEAMPIPE_LOG_LEVEL=debug \
  ghcr.io/devops-ia/steampipe:v2.4.1 \
  steampipe service start --foreground --database-listen network

docker logs -f steampipe
```
