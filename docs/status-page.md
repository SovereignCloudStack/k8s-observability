# Status page monitoring

## Prerequisites

To test the Monitoring of the SCS Status page we expect running Kubernetes cluster that already contains
SCS monitoring platform and Status page deployed in the dedicated `status-page` namespace.

### Local environment use case - KinD/K3s cluster deployed locally

#### KinD

Install the SCS monitoring solution into the KinD Kubernetes cluster following the instructions provided in
the [quickstart guide](quickstart.md).

#### K3s

Install the SCS monitoring solution into the K3s Kubernetes cluster following the instructions provided in
the [k3s guide](k3s.md).

### OSISM use case - K3s cluster in OSISM deployment

[OSISM](https://osism.tech/docs/guides/deploy-guide/services/kubernetes) utilizes the k3s distribution of Kubernetes
as a management cluster for the OSISM IaaS platform. This management cluster is then used as a host for
the SCS monitoring solution. Subsequently, the management cluster becomes an Observer cluster as it hosts
the SCS monitoring solution.
From that point, the Observer cluster observes itself (i.e., k3s cluster control plane components and nodes) and is used
for observing the IaaS layer around the k3s cluster.

In the case of the existing [OSISM IaaS deployment >= 7.0.3](https://osism.tech/docs/release-notes/osism-7#703) on
baremetal, [testbed](https://osism.tech/docs/guides/other-guides/testbed) or [cloud in the box](https://osism.tech/docs/guides/other-guides/cloud-in-a-box)
we expect a management k3s Kubernetes cluster with the deployed SCS monitoring platform.
If your OSISM installation does not meet the above requirements, apply the following plays:
```bash
osism apply kubernetes
osism apply kubernetes-monitoring
```

## Deploy Status page monitoring

This step deploys the Grafana dashboards and instructs the monitoring stack to add the Status Page metrics targets into the Prometheus configuration:

```bash
helm upgrade dnation-kubernetes-monitoring-stack dnationcloud/dnation-kubernetes-monitoring-stack --reset-then-reuse-values -f status-page/status-page-values.yaml
```

- Note: The `--reset-then-reuse-values` option requires Helm v3.14.0 or later. Alternatively, you can use the original values
  by applying `-f values-observer.yaml`, see full command: `helm upgrade dnation-kubernetes-monitoring-stack dnationcloud/dnation-kubernetes-monitoring-stack -f values-observer.yaml -f status-page/status-page-values.yaml`

### Access the Status page dashboards

At this point, you should have the ability to access the Grafana UI, and Status page dashboards.

Log in to the Grafana UI and find the Status page dashboard in `StatusPage` directory:
```bash
http://localhost:30000
```
- Use the following credentials:
  - username: `admin`
  - password: `pass`
