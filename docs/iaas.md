# IaaS monitoring (experimental)

This component is marked as experimental, and it is not part of the reference SCS installation available
at https://monitoring.scs.community.

To test the Monitoring of the IaaS layer use case, follow next steps.
As an example for monitoring of IaaS layer deployment, we utilized `OSISM testbed`.

- Add the IP address of IaaS into the thanos query store to be able to scrape metrics.

```bash
thanos:
  query:
    stores:
    - 213.131.230.77:10901 # testbed IP address as an example of IaaS
```

- Enable IaaS layer in your monitoring, i.e. adjust `values-observer.yaml` as follows:

```bash
dnation-kubernetes-monitoring:
  testbedMonitoring:
    enabled: true
```

- Apply some specific dashboards for `OSISM testbed` as an example of monitoring of IaaS layer deployment:

```bash
kubectl apply -f dashboards/testbed
```
