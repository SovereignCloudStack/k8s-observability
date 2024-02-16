# Zuul monitoring

This page contains instructions on how to enable the Zuul monitoring in the Observer solution. 

Zuul comes with support for the statsd protocol, hence the graphite instance is needed when
we want directly consume Zuul metrics.

Graphite deployment:
```bash
helm add repo kiwigrid https://kiwigrid.github.io
helm upgrade --install graphite kiwigrid/graphite -f zuul/values-zuul.yaml
```

A UDP load balancer that exposes the Graphite receiver service:
```bash
kubectl apply -f zuul/udp-lb-service.yaml
```

Zuul dashboards:
```bash
kubectl apply -f zuul/zuul-status-dashboard.yaml
kubectl apply -f zuul/zuul-nodepool-dashboard.yaml
kubectl create -f zuul/zuul-zookeeper-dashboard.yaml
```

Find and uncomment a related section in `values-observer.yaml` if you want to link the above
dashboards to the L1 Zuul host dashboard. 
The sections related to Zuul in the `values-observer-scs.yaml` values file are already uncommented.
