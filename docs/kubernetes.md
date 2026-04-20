# Kubernetes

This image is designed for the [helm-steampipe](https://github.com/devops-ia/helm-steampipe) Helm chart but also works with plain Kubernetes manifests.

**Helm chart docs:**
- [Installation & GitOps](https://github.com/devops-ia/helm-steampipe/blob/main/docs/installation.md) — OCI, ArgoCD, Flux, RBAC
- [Plugin configuration](https://github.com/devops-ia/helm-steampipe/blob/main/docs/plugins.md) — AWS/GCP/Azure/K8s .spc examples
- [Security & Workload Identity](https://github.com/devops-ia/helm-steampipe/blob/main/docs/security.md) — IRSA, GCP WI, Azure WI, network policies
- [Integrations](https://github.com/devops-ia/helm-steampipe/blob/main/docs/integrations.md) — Grafana, Prometheus, dbt, Python/Node
- [SQL Queries](https://github.com/devops-ia/helm-steampipe/blob/main/docs/queries.md) — AWS, GCP, Azure, Kubernetes, multi-cloud
- [Troubleshooting](https://github.com/devops-ia/helm-steampipe/blob/main/docs/troubleshooting.md) — CrashLoopBackOff, OOM, ingress

## Install with Helm

```bash
helm repo add devops-ia https://devops-ia.github.io/helm-charts
helm repo update

helm install steampipe devops-ia/steampipe \
  --set image.repository=ghcr.io/devops-ia/steampipe \
  --set image.tag=2.4.1 \
  --set bbdd.enabled=true \
  --set bbdd.listen=network \
  --namespace steampipe \
  --create-namespace
```

## Upgrade the image version

```bash
helm upgrade steampipe devops-ia/steampipe \
  --set image.tag=2.5.0 \
  --reuse-values
```

## Custom values file

```yaml
# values.yaml
image:
  repository: ghcr.io/devops-ia/steampipe
  tag: "2.4.1"

bbdd:
  enabled: true
  listen: network
  port: 9193

resources:
  requests:
    cpu: "250m"
    memory: "512Mi"
  limits:
    cpu: "2000m"
    memory: "2Gi"

env:
  - name: STEAMPIPE_MEMORY_MAX_MB
    value: "1536"
  - name: STEAMPIPE_PLUGIN_MEMORY_MAX_MB
    value: "1024"
  - name: STEAMPIPE_DATABASE_PASSWORD
    valueFrom:
      secretKeyRef:
        name: steampipe-credentials
        key: password
```

```bash
helm install steampipe devops-ia/steampipe -f values.yaml \
  --namespace steampipe --create-namespace
```

## Inject plugin credentials via Secrets

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: aws-credentials
  namespace: steampipe
type: Opaque
stringData:
  AWS_ACCESS_KEY_ID: "AKIAIOSFODNN7EXAMPLE"
  AWS_SECRET_ACCESS_KEY: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
  AWS_DEFAULT_REGION: "us-east-1"
```

Reference the Secret in your Helm values:

```yaml
envFrom:
  - secretRef:
      name: aws-credentials
```

## Mount a plugin .spc file via ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: steampipe-plugin-config
  namespace: steampipe
data:
  aws.spc: |
    connection "aws" {
      plugin  = "aws"
      regions = ["us-east-1", "eu-west-1"]
    }
```

Reference it in your Helm values:

```yaml
extraVolumes:
  - name: plugin-config
    configMap:
      name: steampipe-plugin-config

extraVolumeMounts:
  - name: plugin-config
    mountPath: /home/steampipe/.steampipe/config/aws.spc
    subPath: aws.spc
    readOnly: true
```

## Plugin installation via init container

Install plugins before the main container starts using the chart's `initContainer.plugins` value:

```yaml
initContainer:
  plugins:
    - aws
    - azure
    - gcp
```

## OpenShift compatibility

The image runs as **UID 9193 / GID 0** — compatible with OpenShift's restricted Security Context Constraint (SCC) without modifications.

```yaml
# No securityContext overrides needed for OpenShift restricted SCC
securityContext: {}
```

## Health check

The PostgreSQL endpoint serves as the health check:

```yaml
livenessProbe:
  exec:
    command:
      - pg_isready
      - -h
      - localhost
      - -p
      - "9193"
      - -U
      - steampipe
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  exec:
    command:
      - pg_isready
      - -h
      - localhost
      - -p
      - "9193"
      - -U
      - steampipe
  initialDelaySeconds: 15
  periodSeconds: 5
```

## Connect from another pod

```bash
# From any pod in the same namespace
psql -h steampipe -p 9193 -U steampipe -d steampipe

# Using the full service DNS
psql -h steampipe.steampipe.svc.cluster.local -p 9193 -U steampipe -d steampipe
```
