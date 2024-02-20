# SCS Registry monitoring

## Deploy SCS Registry - workload cluster

1. Create necessary issuers and certificates inside the **observer** cluster:

   Note: skip this until [#32](https://github.com/SovereignCloudStack/k8s-observability/issues/32) is resolved
   ```bash
   kubectl apply -f observer/mtls/
   ```
2. Copy created `query-harbor.dnation.cloud` secret to the [workload/server-secret.yaml](./workload/server-secret.yaml)
   and apply to the **workload** cluster:

   Note: skip this until [#32](https://github.com/SovereignCloudStack/k8s-observability/issues/32) is resolved
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

## (Re)Deploy SCS Registry - observer cluster

Note: Uncomment all registry related parts in `values-observer.yaml` and update the
dnation-kubernetes-monitoring-stack deployment.

### Upgrade dnation-kubernetes-monitoring-stack with additional SCS Registry values

```bash
helm upgrade --install dnation-kubernetes-monitoring-stack dnationcloud/dnation-kubernetes-monitoring-stack \
  -f ../values-observer-scs.yaml
```
