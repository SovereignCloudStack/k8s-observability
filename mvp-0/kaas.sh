#!/usr/bin/env bash
# Script creates (in parallel) multiple KinD clusters and bootstraps them with Prometheus-agent based monitoring stack
# ./kaas.sh <action> <number of k8s clusters> <observer kubeconfig>

if [ "$1" = "create" ]; then
  ACTION=$1
elif [ "$1" = "delete" ]; then
  ACTION=$1
else
  echo "ERROR: Not supported kaas action (only create and delete are supported)" >&2; exit 1
fi

if ! [[ $2 =~ ^[0-9]+$ ]] || [[ -z "$2" ]] ; then
  echo "ERROR: Need to define number of KaaS clusters" >&2; exit 1
fi

if [[ -z "$3" ]] || ! [[ -f $3 ]] ; then
  echo "ERROR: Need to provide observer kubeconfig" >&2; exit 1
fi

KAAS_NO=($(seq 1 1 "$2"))

kaas_create() {
  kind create cluster --config kind_cluster_config.yaml --image kindest/node:v1.25.11 --name kaas-"$1"
  echo "KaaS workload cluster kaas-$1 created"
  helm --kube-context kind-kaas-"$1" upgrade --install monitoring prometheus-community/kube-prometheus-stack -f values-workload.yaml --set prometheus.prometheusSpec.externalLabels.cluster=kaas-"$1"
  echo "KaaS workload cluster kaas-$1 bootstrapped with monitoring"
  kubectl --kubeconfig "$3" patch cm kaas-clusters -p '{"data":{"'"kaas-$1"'":""}}'
  echo "KaaS prometheus metric of workload cluster kaas-$1 imported"
}

kaas_delete() {
  kind delete cluster --name kaas-"$1"
  echo "KaaS workload cluster kaas-$1 deleted"
  kubectl --kubeconfig "$3" patch cm kaas-clusters -p '{"data":{"'"kaas-$1"'":null}}'
  echo "KaaS prometheus metric of workload cluster kaas-$1 removed"
}

export -f kaas_create
export -f kaas_delete

parallel --lb kaas_"$ACTION" ::: "${KAAS_NO[@]}"
