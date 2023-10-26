# MVP-0

## Observer cluster

### Deploy dnation-kubernetes-monitoring-stack without dnation-kubernetes-monitoring

1. Fill `thanos-storage.yaml` with bucket credentials
2. Deploy
   ```bash
   helm repo add dnationcloud https://dnationcloud.github.io/helm-hub/
   helm repo update dnationcloud
   helm upgrade --install dnation-kubernetes-monitoring-stack dnationcloud/dnation-kubernetes-monitoring-stack \
     --set dnation-kubernetes-monitoring.enabled=false \
     -f values-observer.yaml \
     -f thanos-storage.yaml
   ```

### Deploy dnation-kubernetes-monitoring

1. Clone and build rules/dashboards
   ```bash
   git clone https://github.com/dNationCloud/kubernetes-monitoring.git
   cd kubernetes-monitoring
   git checkout scs-kaas-mvp
   make jsonnet-package
   cd -
   ```
2. Deploy
   ```bash
   helm upgrade --install dnation-kubernetes-monitoring kubernetes-monitoring/chart --dependency-update \
     --set releaseOverride=dnation-kubernetes-monitoring-stack \
     -f values-observer-dash.yaml
   ```

## Workload cluster

### Create KinD workload cluster

```bash
kind create cluster --config kind_cluster_config.yaml --image kindest/node:v1.25.11 --name workload
```

### Deploy prometheus agent

1. Fill `values-workload.yaml` **remoteWrite url**
2. Deploy
   ```bash
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm repo update prometheus-community
   helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
     -f values-workload.yaml
   ```
