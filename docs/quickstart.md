# Quickstart

These page covers the process of deploying the Observer monitoring solution
into the Kubernetes cluster.

The configuration options used in this tutorial result in a non-productive and simple
deployment of the Observer monitoring solution. The steps do not guide users to register
certain observer targets, such as existing Kubernetes clusters or virtual machines.
Additionally, the tutorial lacks guidance for deploying optional and experimental components
like IaaS and KaaS monitoring. 

At the end of this tutorial, the reader should end up with a Kubernetes cluster where the Observer solution will
be installed and will monitor the Kubernetes cluster hosting it.

## Prerequisites

- [kind](https://kind.sigs.k8s.io/)
- [kubectl](https://kubernetes.io/docs/reference/kubectl/)
- [helm](https://helm.sh/)

## Prepare Kubernetes cluster

```bash
kind create cluster --config kind-observer-config.yaml --image kindest/node:v1.27.3 --name observer
```

If you opt not to use KinD and prefer utilizing an existing Kubernetes cluster,
ensure that the metric endpoints for various control plane components are properly exposed.
Refer to the [docs](https://dnationcloud.github.io/kubernetes-monitoring/helpers/FAQ/#kubernetes-monitoring-shows-or-0-state-for-some-control-plane-components-are-control-plane-components-working-correctly).

## Deploy Observer monitoring solution

```bash
helm repo add dnationcloud https://dnationcloud.github.io/helm-hub/
helm repo update dnationcloud
helm upgrade --install dnation-kubernetes-monitoring-stack dnationcloud/dnation-kubernetes-monitoring-stack -f values-observer.yaml
```

## Access the Observer monitoring UIs

At this point, you should have the ability to access the Grafana, Alertmanager and Thanos UIs
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

- Thanos UI
  ```bash
  http://localhost:30002
  ```
