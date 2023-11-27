# SCS Registry monitoring

## Deploy SCS Registry - workload cluster

1. Create necessary issuers and certificates inside the **observer** cluster:
   ```bash
   kubectl apply -f observer/mtls/
   ```
2. Copy created `query-harbor.dnation.cloud` secret to the [workload/server-secret.yaml](./workload/server-secret.yaml)
   and apply to the **workload** cluster:
   ```bash
   kubectl apply -f workload/server-secret.yaml
   ```
3. Deploy *dnation-kubernetes-monitoring-stack* to the **workload** cluster:
   - Optional: Fill `workload/thanos-objstore.yaml` with bucket credentials in **thanosStorage config**
   - Deploy
   ```bash
   helm upgrade --install dnation-kubernetes-monitoring-stack dnationcloud/dnation-kubernetes-monitoring-stack \
     -f workload/values-workload.yaml \
     -f workload/thanos-objstore.yaml # Optional
   ```

## Deploy SCS Registry - observer cluster

### Upgrade dnation-kubernetes-monitoring-stack with additional SCS Registry values

```bash
helm upgrade --install dnation-kubernetes-monitoring-stack dnationcloud/dnation-kubernetes-monitoring-stack \
  --set dnation-kubernetes-monitoring.enabled=false \
  -f ../values-observer.yaml \
  -f observer/values-observer.yaml \
  -f ../thanos-objstore.yaml  # Optional
```

### Upgrade dnation-kubernetes-monitoring with additional SCS Registry values

```bash
helm upgrade --install dnation-kubernetes-monitoring kubernetes-monitoring/chart \
  --set releaseOverride=dnation-kubernetes-monitoring-stack \
  -f ../values-observer-dash.yaml \
  -f observer/values-observer-dash.yaml
```
