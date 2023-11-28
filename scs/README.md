# SCS Brand

To deploy a rebranded version of Grafana, follow the steps below:

Apply SCS brand customization:
```bash
kubectl apply -f scs/logo.yaml
kubectl apply -f scs/brand.yaml
```
Uncomment the following section in the[values-observer.yaml](../values-observer.yaml) values file:
```yaml
## SCS branding
    extraConfigmapMounts:
      - name: scs-logo
        mountPath: /usr/share/grafana/public/img/scs_logo.svg
        subPath: scs_logo.svg
        configMap: scs-logo
      - name: dnation-home
        mountPath: /usr/share/grafana/public/dashboards/home.json
        subPath: home.json
        configMap: dnation-home
    extraSecretMounts:
      - name: scs-brand
        mountPath: /etc/secrets
        secretName: scs-brand
        defaultMode: 0755
```

The above `brand.yaml` secret was generated from the shell [script](dnation_brand.sh) as follows:
```bash
kubectl create secret generic scs-brand --from-file=dnation_brand.sh --dry-run=client -o yaml
```
