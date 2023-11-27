## Brand

SCS uses re-branded version of Grafana. This is done by basic script which needs to be mounted as k8s secret.
Raw form of scrips is available [here](dnation_brand.sh). If you want to re-generate k8s secret use following:
```bash
kubectl create secret generic scs-brand --from-file=dnation_brand.sh --dry-run=client -o yaml
```
