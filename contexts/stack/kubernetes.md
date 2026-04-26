---
context: stack
name: Kubernetes · Helm
description: K8s deployments, Helm charts, resource limits, healthchecks
---

## Stack Kubernetes / Helm

### Estructura mínima por servicio
```yaml
# Deployment
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
readinessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 5
```

### Siempre
- `resources.requests` y `resources.limits` en todos los containers
- `livenessProbe` + `readinessProbe` en todos los services
- `PodDisruptionBudget` para servicios críticos
- Secrets via `kubectl create secret` o Sealed Secrets — nunca en YAML en repo

### Helm
- Un chart por servicio
- `values.yaml` con defaults seguros
- Secrets desde Vault/Bitwarden → Helm secrets plugin

### Namespaces
- `production`, `staging`, `monitoring` — nunca desplegar en `default`

### Prohibido
- `latest` como tag de imagen
- Containers corriendo como root (`runAsNonRoot: true` obligatorio)
- Secrets en `values.yaml` sin cifrar
