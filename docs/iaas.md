# IaaS monitoring (experimental)

This component is marked as experimental, and it is not part of the reference SCS installation available
at https://monitoring.scs.community.

IaaS monitoring currently integrates and is able to observe the following targets:
- [OpenStack](#openstack)
- [Ceph](#ceph)

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

### OpenStack

#### Prometheus metrics and alerts

The [OpenStack exporter for Prometheus](https://github.com/openstack-exporter) could be deployed using the SCS [openstack-exporter-helm-chart](https://github.com/SovereignCloudStack/openstack-exporter-helm-charts).
This exporter contains a bunch of [Prometheus alerts and rules](https://github.com/SovereignCloudStack/openstack-exporter-helm-charts/blob/master/charts/prometheus-openstack-exporter/templates/prometheusrule.yaml)
that are deployed together with the exporter.
Visit the `iaas/openstack-exporter-values.yaml` file to validate the Helm configuration options.
Ensure valid OpenStack API credentials are set under the `clouds_yaml_config` section. This **MUST** be overridden!

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

#### Grafana dashboards

The Grafana dashboard designed to visualize metrics collected from an OpenStack cloud through the OpenStack exporter
is publicly available at https://grafana.com/grafana/dashboards/21085. Its source code is located in the
`iaas/dashboards` directory. Feel free to import it to the Grafana via its source or ID.
For automatic integration into the SCS monitoring solution proceed to the next step.

#### Update the SCS monitoring deployment

This step deploys the Grafana dashboards and instructs the monitoring stack to add the OpenStack exporter target into the Prometheus configuration:

```bash
helm upgrade dnation-kubernetes-monitoring-stack dnationcloud/dnation-kubernetes-monitoring-stack --reset-then-reuse-values -f iaas/values-observer-iaas.yaml
```

- Note: The `--reset-then-reuse-values` option requires Helm v3.14.0 or later. Alternatively, you can use the original values
  by applying `-f values-observer.yaml`, see full command: `helm upgrade dnation-kubernetes-monitoring-stack dnationcloud/dnation-kubernetes-monitoring-stack -f values-observer.yaml -f iaas/values-observer-iaas.yaml`

#### Access the OpenStack dashboard

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

### Ceph

The SCS IaaS reference implementation (OSISM) currently supports [ceph-ansible](https://github.com/ceph/ceph-ansible)
method for deploying Ceph. Support for the [rook operator](https://github.com/rook/rook) deployment method will be available [soon](https://github.com/osism/issues/issues/881).

This guide covers Ceph cluster monitoring for both deployment methods. While both expose the same metrics via the same
endpoint, there are some differences in Prometheus configuration and alerts.

#### Prometheus metrics and alerts

Ceph contains 2 build-in sources of metrics a.k.a. exporters.
The Ceph exporter (introduced in Reef release of Ceph) is the main source of Ceph performance metrics. It runs as a
dedicated daemon. This daemon runs on every Ceph cluster host and exposes a metrics end point where all the performance
counters exposed by all the Ceph daemons running in the host are published in the form of Prometheus metrics.

The second source of metrics is the Prometheus manager module. It exposes metrics related to the whole cluster,
basically metrics that are not produced by individual Ceph daemons.

Read the related Ceph [docs](https://docs.ceph.com/en/reef/monitoring/#ceph-metrics).
Since these exporters are integrated with Ceph, deploying a third-party Ceph exporter is unnecessary.

**Prometheus alerts**

Both Ceph deployment strategies use the ceph-mixins project as a source of alerts. The ceph-ansible and rook projects
each maintain a rendered version of these alerts, but the rook repository contains some differences, primarily because
rook does not use the cephadm tool as a backend. 
Therefore, find and apply one of the following commands to create a custom observer rules values file for either the
ceph-ansible or ceph-rook deployment ([yq](https://github.com/mikefarah/yq/#install) tool required):

```bash
# ceph-ansible
curl -s https://raw.githubusercontent.com/ceph/ceph/main/monitoring/ceph-mixin/prometheus_alerts.yml | \
  yq '{"kube-prometheus-stack": {"additionalPrometheusRulesMap": {"ceph-rook-rules": (. + {"additionalLabels": {"prometheus_rule": "1"}})}}}' > iaas/values-observer-ceph-rules.yaml

# rook
curl -s https://raw.githubusercontent.com/rook/rook/master/deploy/charts/rook-ceph-cluster/prometheus/localrules.yaml | \
  yq '{"kube-prometheus-stack": {"additionalPrometheusRulesMap": {"ceph-rook-rules": (. + {"additionalLabels": {"prometheus_rule": "1"}})}}}' > iaas/values-observer-ceph-rules.yaml
```

#### Grafana dashboards

We've tested and could recommend 2 sources of Grafana dashboards that are suitable for both Ceph deployment strategies (ansible and rook):
- [dashboards linked in rook docs](https://rook.io/docs/rook/latest-release/Storage-Configuration/Monitoring/ceph-monitoring/?h=gra#grafana-dashboards)
- [ceph-mixins dashboards](https://github.com/ceph/ceph-mixins/tree/master/dashboards)
  - Built version of ceph-mixins dashboards could be found e.g. [here](https://github.com/ceph/ceph/tree/main/monitoring/ceph-mixin/dashboards_out)

We consider the dashboards created within the Rook project as a solid starting point for Ceph metrics visualization.
If you want to see more detailed dashboards, uncomment and use the ceph-mixin dashboards in the `values-observer-ceph-rook.yaml`
or `values-observer-ceph-ansible.yaml` file. You can use both.

#### Update the SCS monitoring deployment

This step deploys Grafana dashboards, Prometheus rules and instruct monitoring stack to add the Ceph exporter targets into the Prometheus configuration.
Ensure that you add the monitoring targets' IPs and ports to `values-observer-ceph-ansible.yaml` for Ceph-ansible deployments/

```bash
helm upgrade dnation-kubernetes-monitoring-stack dnationcloud/dnation-kubernetes-monitoring-stack --reset-then-reuse-values \
  -f iaas/values-observer-ceph-rules.yaml \
  -f iaas/values-observer-ceph-[rook|ansible].yaml  # use values file for either the ceph-ansible or ceph-rook deployment
```

- Note: The `--reset-then-reuse-values` option requires Helm v3.14.0 or later. Alternatively, you can use the original values
  by applying `-f values-observer.yaml`, see full command: `helm upgrade dnation-kubernetes-monitoring-stack dnationcloud/dnation-kubernetes-monitoring-stack -f values-observer.yaml -f iaas/values-observer-ceph-rules.yaml -f iaas/values-observer-ceph-[rook|ansible].yaml`
