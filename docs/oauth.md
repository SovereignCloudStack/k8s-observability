# OAUTH

We set up oauth2 with GitHub provider for the https://monitoring.scs.community according to the https://kubernetes.github.io/ingress-nginx/examples/auth/oauth-external-auth/.

To use it, inspect `oauth/oauth2-proxy.yaml` and modify it according to your needs.
You want to change at least these:
- OAUTH2_PROXY_CLIENT_ID
- OAUTH2_PROXY_CLIENT_SECRET
- OAUTH2_PROXY_COOKIE_SECRET
- ingress host

Then deploy oauth2-proxy as follows:
```bash
kubectl apply -f oauth/oauth2-proxy.yaml
```

We set up OAuth authentication for these components:
- Thanos Query
  - it is exposed via ingress on monitoring.scs.community/thanos
  - modified with `--web.external-prefix=thanos` extra flag
    - ruler query endpoint and grafana datasource url need to be modified
- Alertmanager
  - it is exposed via ingress on monitoring.scs.community/alertmanager
  - modified with `routePrefix: /alertmanager` alertmanagerSpec
    - ruler alertmanager url needs to be modified

You have to also uncomment a related sections in `values-observer.yaml` for exposing
the components via ingress.
The sections related to OAUTH in the `values-observer-scs.yaml` values file are already uncommented.
