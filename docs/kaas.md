# KaaS monitoring (experimental)

This component is marked as experimental, and it is not part of the reference SCS installation available
at https://monitoring.scs.community.

To test the Monitoring of the KaaS layer use case, deploy the Kaas-metric-importer
into the Observer cluster.

The Kaas-metric-importer is a simple service through which the KaaS software registers
and unregisters newly created or deleted KaaS clusters in the Observer monitoring.
This functionality enables the Observer monitoring to differentiate between KaaS clusters deleted intentionally
and those that have stopped writing metrics to the Observer monitoring for any reason.

```bash
kubectl apply -f ../kaas-metric-importer.yaml
```

The Kaas-metric-importer uses an image built from https://github.com/m3dbx/prometheus_remote_client_golang.
It has mounted configmap and based on configmap keys it pushes custom metric `kaas`
with label `cluster` and value `1` into the thanos receiver.

Example of configmap:
```yaml
data:
  workload-cluster: ""
```
It pushes metric e.g. `kaas{cluster="workload-cluster"} 1` to the Observer.
It is important to keep the configmap up-to-date with your KaaS offering. This is automated e.g. 
in the KaaS mock service below.

## KaaS mock service

To evaluate the Monitoring of the KaaS layer use case and view actual metrics in your
Observer monitoring cluster, you can launch the KaaS mock service.

Put your Observer monitoring cluster kubeconfig into the `./kaas/manifests/` directory and name
it `observer-kubeconfig.yaml` (or adjust kaas service `./kaas/app/config.py` accordingly).

If you're utilizing the KinD Observer deployment outlined in this tutorial, collect the kubeconfig using the following command:
```bash
kind get kubeconfig --name observer > ./kaas/manifests/observer-kubeconfig.yaml
```

All KaaS mock service dependencies can be installed via the corresponding `./kaas/requirements.txt` file.
Installing them into a Python virtualenv is recommended.

```bash
cd kaas
python3 -m venv .venv  # Optional
source .venv/bin/activate  # Optional
# Install kaas dependencies
pip install -r requirements.txt

# Launch the KaaS mock service
make kaas
```

At this point, you should have the ability to access the KaaS mock service Swagger UI:

```bash
http://127.0.0.1:8080/kaas
```

- Create KaaS cluster through Swagger UI: [Create Cluster](http://127.0.0.1:8080/kaas#/Clusters/create_cluster_api_clusters__post) or
  call directly the KaaS service API via some client, e.g.:
  ```bash
  curl -X POST -H "Content-Type: application/json" http://127.0.0.1:8080/api/clusters/ -d '{"name": "kaas"}'
  ```

  Navigate to the [KaaS Monitoring dashboard](http://localhost:30000/d/kaas-monitoring/kaas-monitoring)
  in the Observer monitoring. After a few minutes (approximately 4), your KaaS cluster should become visible.
  Click on the cluster box to dive into KaaS cluster dashboards at a more detailed level.
  Repeat the process to explore further and gain deeper insights.

  Note: The disk utilization expression for the Docker environment has not been adjusted,
  so you will encounter non-realistic numbers in the nodes/disk sections. However,
  the other sections should accurately reflect the reality.

- Retrieve a list of all KaaS clusters and check their status. Swagger UI: [Get List of Clusters](http://127.0.0.1:8080/kaas#/Clusters/get_clusters_api_clusters__get) or
  call directly the KaaS service API via some client, e.g.:
  ```bash
  curl -s -X GET -H 'accept: application/json' http://127.0.0.1:8080/api/clusters/
  ```

- Get Kaas Cluster kubeconfig by its name through Swagger UI: [Get Cluster kubeconfig](http://127.0.0.1:8080/kaas#/Clusters/get_kubeconfig_api_clusters__name__get) or
  call directly the KaaS service API via some client and save it, e.g.:
  ```bash
  curl -s -X GET -H 'accept: application/json' http://127.0.0.1:8080/api/clusters/kaas > kaas-kube
  ```

- Now, you have the opportunity to play with your KaaS cluster and experiment with triggering
  monitoring alerts by initiating actions like destroying certain components 😎.
  ```bash
  kubectl --kubeconfig kaas-kube get po -A
  ```

- Finally, delete your KaaS cluster by its name through Swagger UI: [Delete Cluster](http://127.0.0.1:8080/kaas#/Clusters/delete_cluster_api_clusters__delete) or
  call directly the KaaS service API via some client and save it, e.g.:
  ```bash
  curl -X DELETE http://127.0.0.1:8080/api/clusters/?name=kaas
  ```
