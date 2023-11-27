#!/usr/bin/env bash
# Script creates (in parallel) multiple KaaS clusters
# ./kaas.sh <action> <number of k8s clusters>

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

KAAS_NO=($(seq 1 1 "$2"))

kaas_create() {
  curl -s -X POST -H "Content-Type: application/json" http://127.0.0.1:8080/api/clusters/ -d '{"name": "'"kaas-$1"'"}'
  echo "KaaS workload cluster kaas-$1 created"
}

kaas_delete() {
  curl -s -X DELETE http://127.0.0.1:8080/api/clusters/?name="kaas-$1"
  echo "KaaS prometheus metric of workload cluster kaas-$1 removed"
}

export -f kaas_create
export -f kaas_delete

parallel --lb kaas_"$ACTION" ::: "${KAAS_NO[@]}"
