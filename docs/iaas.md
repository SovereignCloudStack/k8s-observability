# IaaS monitoring (experimental)

This component is marked as experimental, and it is not part of the reference SCS installation available
at https://monitoring.scs.community.

## Prerequisites

To test the Monitoring of the IaaS layer we expect running Kubernetes cluster that already contains
SCS monitoring platform.

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

## Deploy IaaS monitoring components

### OpenStack exporter

The [OpenStack exporter for Prometheus](https://github.com/openstack-exporter) could be deployed using the SCS [openstack-exporter-helm-chart](https://github.com/SovereignCloudStack/openstack-exporter-helm-charts).
Visit the `iaas/openstack-exporter-values.yaml` file to validate the Helm configuration options.
Ensure valid OpenStack API credentials are set under the `clouds_yaml_config` section. This MUST be overridden!

```bash
helm upgrade --install prometheus-openstack-exporter oci://registry.scs.community/openstack-exporter/prometheus-openstack-exporter \
  --version 0.4.5 \
  -f iaas/openstack-exporter-values.yaml # --set "endpoint_type=public" --set "serviceMonitor.scrapeTimeout=1m"
```

Tip: If you want to test the exporter basic functionality with **public** OpenStack API, configure `endpoint_type`
to `public` (`--set "endpoint_type=public"`). Note that configuring `endpoint_type` as `public` will result in
incomplete functionality for the Grafana dashboard.

Tip: Requesting and collecting metrics from the OpenStack API can be time-consuming, especially if the API is not
performing well. In such cases, you may observe timeouts on the Prometheus server when it tries to fetch OpenStack
metrics. To mitigate this, consider increasing the scrape interval to e.g. 1 minute (`--set "serviceMonitor.scrapeTimeout=1m"`).

### OpenStack exporter Grafana dashboard

The Grafana dashboard designed to visualize metrics collected from an OpenStack cloud through the OpenStack exporter
is publicly available at https://grafana.com/grafana/dashboards/21085. Its source code is located in the
`iaas/dashboards` directory. Feel free to import it to the Grafana via its source or ID.
For automatic integration into the SCS monitoring solution proceed to the next step.

### Deploy OpenStack exporter Grafana dashboard and instruct monitoring stack to register the OpenStack exporter

Deploy OpenStack exporter Grafana dashboard via its ID and instruct monitoring stack to register the OpenStack exporter
ServiceMonitor via its label as follows:

```bash
helm upgrade dnation-kubernetes-monitoring-stack dnationcloud/dnation-kubernetes-monitoring-stack --reset-then-reuse-values -f iaas/values-observer-iaas.yaml
```

Note: The `--reset-then-reuse-values` option requires Helm v3.14.0 or later. Alternatively, you can use the original values
by applying `-f values-observer.yaml`, see full command:
```bash
helm upgrade dnation-kubernetes-monitoring-stack dnationcloud/dnation-kubernetes-monitoring-stack -f values-observer.yaml -f iaas/values-observer-iaas.yaml
```

### Access the OpenStack dashboard

At this point, you should have the ability to access the Grafana UI, and OpenStack dashboard.

Log in to the Grafana UI and find the OpenStack dashboard in IaaS directory:
```bash
http://localhost:30000
```
or directly access the OpenStack dashboard:
```bash
http://localhost:30000/d/openstack-overview
```

- Use the following credentials:
  - username: `admin`
  - password: `pass`
