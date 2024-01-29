# Zuul monitoring

Zuul comes with support for the statsd protocol, hence the graphite instance is needed when
we want directly consume Zuul metrics.

Graphite deployment:
```bash
helm add repo kiwigrid https://kiwigrid.github.io
helm upgrade --install graphite kiwigrid/graphite -f values-zuul.yaml
```

A UDP load balancer that exposes the Graphite receiver service:
```bash
kubectl apply -f udp-lb-service.yaml
```

Zuul dashboards:
```bash
kubectl apply -f zuul-status-dashboard.yaml
kubectl apply -f zuul-nodepool-dashboard.yaml
kubectl create -f zuul-zookeeper-dashboard.yaml
```

Find and uncomment a related section in `values-observer-dash.yaml` if you want to link the above
dashboards to the L1 Zuul host dashboard.
