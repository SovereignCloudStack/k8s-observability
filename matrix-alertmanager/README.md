# Alertmanager notifications in Matrix chat

Project https://github.com/metio/matrix-alertmanager-receiver is used for forwarding alerts to a Matrix room.

To use it, fill your matrix credentials in [matrix-alertmanager-receiver.yaml](matrix-alertmanager-receiver.yaml)
ConfigMap and deploy:
```bash
kubectl apply -f matrix-alertmanager-receiver.yaml
```
You can modify other settings according to the mentioned project [docs](https://github.com/metio/matrix-alertmanager-receiver)
in the ConfigMap.

You have to also uncomment a related section in [values-observer.yaml](../values-observer.yaml) alertmanager section.
