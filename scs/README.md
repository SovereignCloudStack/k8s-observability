# SCS Brand

The `brand.yaml` secret is generated from the shell [script](dnation_brand.sh) as follows:
```bash
kubectl create secret generic scs-brand --from-file=dnation_brand.sh --dry-run=client -o yaml
```
