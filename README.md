# :mag: k8s-observability 

This repository aims to build an Observer monitoring solution intended to offer a global **metrics**
view of the CSP infrastructure. It is the platform where CSP infrastructure **metrics**
are fetched, processed, stored, and visualized. Note that this monitoring solution could
be extended, and the other two observability signals (logs and traces) from the CSP
infrastructure could also be processed here.

_This repository builds a base for an Observer monitoring solution intended to become an **SCS product**
in the future versions, once it attains sufficient stability._

The current state implements the initial iteration of the Observer monitoring solution,
deployed in the Kubernetes cluster, subsequently referred to as the Observer cluster.
As illustrative examples of how this monitoring solution can be utilized, the initial version also
implements three use cases:
- Monitoring of the KaaS layer
- Monitoring of the IaaS layer
- Monitoring of infrastructure services (such as CSP services deployed on top of the IaaS layer)

_The monitoring stack employed for observing the KaaS layer and infrastructure services
is designed to serve as an **SCS product** in the future versions, once it attains sufficient stability.
This is because the monitoring focuses on elements like Kubernetes clusters and infrastructure
services, utilizing Kubernetes API and protocols such as HTTP(S), TCP, ICMP, etc.,
which are aspects CSPs are unlikely to alter._

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
`thanos-storage.yaml` template manifest with the credentials for the object store
(refer to `thanosStorage.config`).

```bash
helm repo add dnationcloud https://dnationcloud.github.io/helm-hub/
helm repo update dnationcloud
helm upgrade --install dnation-kubernetes-monitoring-stack dnationcloud/dnation-kubernetes-monitoring-stack \
  --set dnation-kubernetes-monitoring.enabled=false \
  -f values-observer.yaml \
  -f thanos-storage.yaml  # Optional
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

To evaluate the Monitoring of the KaaS layer use case and view actual metrics in your
Observer monitoring cluster, you can launch the KaaS mock service (refer to the [kaas](./kaas) directory).

Put your Observer monitoring cluster kubeconfig into the `kaas/manifests/` directory and name
it `observer-kubeconfig.yaml` (or adjust kaas service [configuration](./kaas/app/config.py) accordingly).

If you're utilizing the KinD Observer deployment outlined in this tutorial, collect the kubeconfig using the following command:
```bash
kind get kubeconfig --name observer > kaas/manifests/observer-kubeconfig.yaml
```

All KaaS mock service dependencies can be installed via the corresponding `requirements.txt` file.
Installing them into a Python virtualenv is recommended.

```bash
cd kaas
python3 -m venv .venv  # Optional
source .venv/bin/activate  # Optional
# Install kaas dependencies
pip install -r requirements.txt

# Launch the KaaS mock service
make kaas
```

At this point, you should have the ability to access the KaaS mock service Swagger UI:

```bash
http://127.0.0.1:8080/kaas
```

- Create KaaS cluster through Swagger UI: [Create Cluster](http://127.0.0.1:8080/kaas#/Clusters/create_cluster_api_clusters__post) or
  call directly the KaaS service API via some client, e.g.:
  ```bash
  curl -X POST -H "Content-Type: application/json" http://127.0.0.1:8080/api/clusters/ -d '{"name": "kaas"}'
  ```

  Navigate to the [KaaS Monitoring dashboard](http://localhost:30000/d/kaas-monitoring/kaas-monitoring)
  in the Observer monitoring. After a few minutes (approximately 4), your KaaS cluster should become visible.
  Click on the cluster box to dive into KaaS cluster dashboards at a more detailed level.
  Repeat the process to explore further and gain deeper insights.

  Note: The disk utilization expression for the Docker environment has not been adjusted,
  so you will encounter non-realistic numbers in the nodes/disk sections. However,
  the other sections should accurately reflect the reality.

- Retrieve a list of all KaaS clusters and check their status. Swagger UI: [Get List of Clusters](http://127.0.0.1:8080/kaas#/Clusters/get_clusters_api_clusters__get) or
  call directly the KaaS service API via some client, e.g.:
  ```bash
  curl -s -X GET -H 'accept: application/json' http://127.0.0.1:8080/api/clusters/
  ```

- Get Kaas Cluster kubeconfig by its name through Swagger UI: [Get Cluster kubeconfig](http://127.0.0.1:8080/kaas#/Clusters/get_kubeconfig_api_clusters__name__get) or
  call directly the KaaS service API via some client and save it, e.g.:
  ```bash
  curl -s -X GET -H 'accept: application/json' http://127.0.0.1:8080/api/clusters/kaas > kaas-kube
  ```

- Now, you have the opportunity to play with your KaaS cluster and experiment with triggering
  monitoring alerts by initiating actions like destroying certain components 😎.
  ```bash
  kubectl --kubeconfig kaas-kube get po -A
  ```

- Finally, delete your KaaS cluster by its name through Swagger UI: [Delete Cluster](http://127.0.0.1:8080/kaas#/Clusters/delete_cluster_api_clusters__delete) or
  call directly the KaaS service API via some client and save it, e.g.:
  ```bash
  curl -X DELETE http://127.0.0.1:8080/api/clusters/?name=kaas
  ```

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
