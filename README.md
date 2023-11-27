# :mag: k8s-observability 

This repository aims to build an Observer monitoring solution intended to offer a global **metrics**
view of the CSP infrastructure. It is the platform where CSP infrastructure **metrics**
are fetched, processed, stored, and visualized. Note that this monitoring solution could
be extended, and the other two observability signals (logs and traces) from the CSP
infrastructure could also be processed here.

_This repository builds a base for an Observer monitoring solution intended to become an **SCS product**
in the future versions, once it attains sufficient stability. Currently, it is not
intended for deployment in production environments._

The current state implements the initial iteration of the Observer monitoring solution,
deployed in the Kubernetes cluster, subsequently referred to as the Observer cluster.
As illustrative examples of how this monitoring solution can be utilized, the initial version also
implements three use cases:
- Monitoring of the KaaS layer
- Monitoring of the IaaS layer
- Monitoring of infrastructure services (such as CSP services deployed on top of the IaaS layer)

_The monitoring stack employed for observing the KaaS layer and infrastructure services
is designed to serve as an **SCS product** in the future versions, once it attains sufficient stability.

TODO: insert a high leve; arch. diagram here

# Deployment

These deployment steps cover the process of deploying the Observer monitoring solution
into the Kubernetes cluster. Additionally, they provide optional guidance for deploying
a KaaS mock service, showcasing the Monitoring of the KaaS layer use case. Furthermore,
there is an optional guide for deploying the blackbox exporter, enabling the monitoring
of infrastructure endpoint availability.
The monitoring of the IaaS layer use case is beyond the scope of these deployment steps.


## Prerequisites

- [kind](https://kind.sigs.k8s.io/)
- [kubectl](https://kubernetes.io/docs/reference/kubectl/)
- [helm](https://helm.sh/)
- [jsonnet](https://github.com/google/go-jsonnet)
- [python 3.8+](https://www.python.org/) - needed for Monitoring of the KaaS layer use case
- [make](https://www.gnu.org/software/make/)
- [git](https://git-scm.com/)

## Observer monitoring deployment

### Create Kubernetes cluster

```bash
kind create cluster --config kind-observer-config.yaml --image kindest/node:v1.25.11 --name observer
```

If you opt not to use KinD and prefer utilizing an existing Kubernetes cluster,
ensure that the metric endpoints for various control plane components are properly exposed.
Refer to the [docs](https://dnationcloud.github.io/kubernetes-monitoring/helpers/FAQ/#kubernetes-monitoring-shows-or-0-state-for-some-control-plane-components-are-control-plane-components-working-correctly).

### Deploy dnation-kubernetes-monitoring-stack without dnation-kubernetes-monitoring

Deploy dnation-kubernetes-monitoring-stack with SCS variables:

_Optional_: Configure the object store as a long-term storage for metrics. Fill the
`thanos-objstore.yaml` template manifest with the bucket credentials (refer to `thanosStorage.config`).

```bash
helm repo add dnationcloud https://dnationcloud.github.io/helm-hub/
helm repo update dnationcloud
helm upgrade --install dnation-kubernetes-monitoring-stack dnationcloud/dnation-kubernetes-monitoring-stack \
  --set dnation-kubernetes-monitoring.enabled=false \
  -f values-observer.yaml \
  -f thanos-objstore.yaml  # Optional
```

### Deploy dnation-kubernetes-monitoring

Clone the 'dnation-kubernetes-monitoring' repository (the SCS branch), and
generate rules and dashboards from Jsonnet code.
```bash
git clone -b scs-kaas-mvp https://github.com/dNationCloud/kubernetes-monitoring.git
cd kubernetes-monitoring
make jsonnet-package
cd -
```
Deploy
```bash
helm upgrade --install dnation-kubernetes-monitoring kubernetes-monitoring/chart --dependency-update \
  --set releaseOverride=dnation-kubernetes-monitoring-stack \
  -f values-observer-dash.yaml
```

### Optional: Monitoring of the KaaS layer deployment

To test the Monitoring of the KaaS layer use case, deploy the Kaas-metric-importer
into the Observer cluster.

The Kaas-metric-importer is a simple service through which the KaaS software registers
and unregisters newly created or deleted KaaS clusters in the Observer monitoring.
This functionality enables the Observer monitoring to differentiate between KaaS clusters deleted intentionally
and those that have stopped writing metrics to the Observer monitoring for any reason.

```bash
kubectl apply -f kaas-metric-importer.yaml
```

The Kaas-metric-importer uses an image built from https://github.com/m3dbx/prometheus_remote_client_golang.
It has mounted configmap and based on configmap keys it pushes custom metric `kaas`
with label `cluster` and value `1` into thanos receiver.
E.g. configmap:
```yaml
data:
  workload-cluster: ""
```
It pushes metric e.g. `kaas{cluster="workload-cluster"} 1` to the Observer.


### Optional: Monitoring of infrastructure services deployment

If you want to monitor the availability of infrastructure services or endpoints by probing
them using protocols such as HTTP, HTTPS, ICMP, DNS, TCP you can deploy `blackbox exporter`
into the Observer cluster via helm chart:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update prometheus-community
helm upgrade --install black-box prometheus-community/prometheus-blackbox-exporter \
-f values-blackbox.yml # example of blackbox values
```
If you want a nice dashboard for monitoring `HTTP` and `HTTPS` endpoints, just apply `blackbox-dashboard.yaml` manifest into the Observer cluster as follows:
```bash
kubectl apply -f blackbox-dashboard.yaml
```

### Access Observer monitoring Grafana UI

At this point, you should have the ability to access the Grafana and Alertmanager UIs
within the Observer monitoring cluster.

- Grafana UI
  ```bash
  http://localhost:30000
  ```
  - Use the following credentials:
    - username: `admin`
    - password: `pass`

- Alertmanager UI
  ```bash
  http://localhost:30001
  ```

## Monitoring of the KaaS layer use case

Refer to [kaas README file](./kaas/README.md).

## Monitoring of infrastructure services (container registry)

Refer to [registry README file](./registry/README.md).

# References

Refer to the links of pull requests, branches, or repositories containing SCS related code:
- [SovereignCloudStack/k8s-observability](https://github.com/SovereignCloudStack/k8s-observability) repository
- [osism/testbed/#1855](https://github.com/osism/testbed/pull/1855)
- [osism/ansible-collection-services/#1221](https://github.com/osism/ansible-collection-services/pull/1221)
- [dNationCloud/kubernetes-monitoring](https://github.com/dNationCloud/kubernetes-monitoring) branch [scs-kaas-mvp](https://github.com/dNationCloud/kubernetes-monitoring/compare/main...scs-kaas-mvp)
- [dNationCloud/kubernetes-monitoring-stack](https://github.com/dNationCloud/kubernetes-monitoring-stack) PRs:
  - [#81](https://github.com/dNationCloud/kubernetes-monitoring-stack/pull/81)
  - [#82](https://github.com/dNationCloud/kubernetes-monitoring-stack/pull/82)
  - [#83](https://github.com/dNationCloud/kubernetes-monitoring-stack/pull/83)
  - [#84](https://github.com/dNationCloud/kubernetes-monitoring-stack/pull/84)
  - [#87](https://github.com/dNationCloud/kubernetes-monitoring-stack/pull/87)
  - [#88](https://github.com/dNationCloud/kubernetes-monitoring-stack/pull/88)
  - [#89](https://github.com/dNationCloud/kubernetes-monitoring-stack/pull/89)
  - [#90](https://github.com/dNationCloud/kubernetes-monitoring-stack/pull/90)
