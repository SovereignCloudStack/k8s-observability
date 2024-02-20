# Infrastructure service endpoints 

This page contains instructions on how to enable probing of infrastructure service endpoints using [blackbox exporter](https://github.com/prometheus/blackbox_exporter).

Infrastructure service endpoints can be probed using protocols such as HTTP, HTTPS, DNS, TCP, ICMP, and gRPC.

Blackbox exporter is a component of the [monitoring stack](https://github.com/dNationCloud/kubernetes-monitoring-stack).
Therefore, it can be deployed into the Observer cluster and configured simply by using the Helm chart values.

To enable probing of infrastructure service endpoints with blackbox exporter, locate and uncomment the related section in `values-observer.yaml`.
The sections related to blackbox exporter in the `values-observer-scs.yaml` values file are already uncommented.
