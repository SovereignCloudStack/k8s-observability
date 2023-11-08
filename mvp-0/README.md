# MVP-0

## Deployment

### Observer cluster

#### Deploy dnation-kubernetes-monitoring-stack without dnation-kubernetes-monitoring

1. Optional: Fill `thanos-storage.yaml` with bucket credentials in **thanosStorage config**
2. Deploy
   ```bash
   helm repo add dnationcloud https://dnationcloud.github.io/helm-hub/
   helm repo update dnationcloud
   helm upgrade --install dnation-kubernetes-monitoring-stack dnationcloud/dnation-kubernetes-monitoring-stack \
     --set dnation-kubernetes-monitoring.enabled=false \
     -f values-observer.yaml \
     -f thanos-storage.yaml # Optional
   ```

#### Deploy dnation-kubernetes-monitoring

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

#### Deploy kaas-metric-importer

Deployment uses an image built from https://github.com/m3dbx/prometheus_remote_client_golang.
It has mounted configmap and based on configmap keys it pushes custom metric `kaas`
with label `cluster` and value `1` into thanos receiver.
E.g. configmap:
```yaml
data:
  workload-cluster: ""
```
It pushes metric `kaas{cluster="workload-cluster"} 1`.

1. Deploy
   ```bash
   kubectl apply -f kaas-metric-importer.yaml
   ```
#### Deploy Blackbox exporter
If you want to monitor the availability and performance of external services or endpoints by probing them using protocols such as HTTP, HTTPS, ICMP, DNS, TCP you can install `blackbox exporter` via helm chart:

```bash
helm upgrade --install black-box prometheus-community/prometheus-blackbox-exporter \
-f values-blackbox.yml # example of blackbox values
```
If you want a nice dashboard for monitoring `HTTP` and `HTTPS` endpoints, you can import into Grafana this [dashboard](https://grafana.com/grafana/dashboards/13659-blackbox-exporter-http-prober/).

### Workload cluster

#### Deploy prometheus agent

1. Fill `values-workload.yaml` **remoteWrite url**
2. Deploy
   ```bash
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm repo update prometheus-community
   helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
     -f values-workload.yaml
   ```

#### Patch kaas-clusters configmap in the observer cluster

1. Take **externalLabels cluster** from `values-workload.yaml`
2. Patch
   ```bash
   kubectl patch cm kaas-clusters -p '{"data":{"workload-cluster":""}}'
   ```

## Quick local deployment

### Observer
Create observer cluster in KinD, see [Observer cluster](#observer-cluster) for more.

Run:
```bash
kind create cluster --config kind_cluster_config.yaml --image kindest/node:v1.25.11 --name observer

helm --kube-context kind-observer upgrade --install dnation-kubernetes-monitoring-stack dnationcloud/dnation-kubernetes-monitoring-stack \
  --set dnation-kubernetes-monitoring.enabled=false \
  -f values-observer.yaml

helm --kube-context kind-observer upgrade --install dnation-kubernetes-monitoring kubernetes-monitoring/chart \
  --set releaseOverride=dnation-kubernetes-monitoring-stack \
  -f values-observer-dash.yaml

kubectl --context kind-observer apply -f kaas-metric-importer.yaml
```

### Workload
Create workload cluster in KinD, see [Workload cluster](#workload-cluster) for more.

Fill `values-workload.yaml` **remoteWrite url** with *http://observer-control-plane:30291/api/v1/receive* and run:
```bash
kind create cluster --config kind_cluster_config.yaml --image kindest/node:v1.25.11 --name workload

helm --kube-context kind-workload upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  -f values-workload.yaml

kubectl --context kind-observer patch cm kaas-clusters -p '{"data":{"workload-cluster":""}}'
```
