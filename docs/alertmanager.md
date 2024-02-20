# Alertmanager notifications in Matrix chat

This page contains instructions on how to enable the Alertmanager to Matrix chat notifications in the Observer solution. 

Project https://github.com/metio/matrix-alertmanager-receiver is used for forwarding alerts to a Matrix room.

To use it, fill your matrix credentials in `matrix-alertmanager/matrix-alertmanager-receiver.yaml` ConfigMap and deploy it:
```bash
kubectl apply -f matrix-alertmanager/matrix-alertmanager-receiver.yaml
```

You can modify other settings according to the mentioned project [docs](https://github.com/metio/matrix-alertmanager-receiver)
in the ConfigMap.

You have to also uncomment a related section in `values-observer.yaml` alertmanager section.
The sections related to Alertmanager notifications in the `values-observer-scs.yaml` values file are already uncommented.
