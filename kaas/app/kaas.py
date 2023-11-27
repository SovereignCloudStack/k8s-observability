import asyncio

import yaml
from typing import List
from loguru import logger

from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter

from . import models
from .database import get_db
from .config import settings

router = APIRouter()


async def wait_for_cluster(cluster_name: str):
    process = await asyncio.create_subprocess_exec(
        "kubectl",
        "cluster-info",
        "--context",
        f"kind-{cluster_name}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    resp, err = await process.communicate()
    if err:
        logger.info(f"The cluster {cluster_name} is not ready yet: {err.decode()}")
        return False

    if "is running" in resp.decode():
        logger.info(f"The cluster {cluster_name} is ready.")
        return True

    return False


async def bootstrap_cluster():
    db = next(get_db())

    clusters = db.query(models.Cluster).all()
    for cluster in clusters:
        if cluster.status == models.ClusterStatus.created:
            continue

        if not await wait_for_cluster(cluster.name):
            logger.info(
                f"The provisioning of the cluster {cluster.name} is in progress."
            )
            continue

        if (
            await wait_for_cluster(cluster.name)
            and cluster.status == models.ClusterStatus.provisioning
        ):
            try:
                await asyncio.create_subprocess_exec(
                    "helm",
                    "--kube-context",
                    f"kind-{cluster.name}",
                    "upgrade",
                    "--install",
                    "monitoring",
                    "prometheus-community/kube-prometheus-stack",
                    "-f",
                    settings.KAAS_MONITORING_CONFIG,
                    "--set",
                    f"prometheus.prometheusSpec.externalLabels.cluster={cluster.name}",
                    "--set",
                    f"prometheus.prometheusSpec.remoteWrite[0].url={settings.OBSERVER_REMOTE_WRITE_URL}",
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                await asyncio.create_subprocess_exec(
                    "kubectl",
                    "--kubeconfig",
                    settings.OBSERVER_KUBECONFIG,
                    "patch",
                    "cm",
                    "kaas-clusters",
                    "-p",
                    f'{{"data":{{"{cluster.name}":""}}}}',
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
            except OSError as err:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Subprocess error: {err}.",
                )
            cluster.status = models.ClusterStatus.created
            db.commit()
            logger.info(f"The bootstrapping of the cluster {cluster.name} is done.")
    db.close()


@router.get(
    "/",
    summary="Get List of Clusters",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=List[models.ClusterSchema],
)
def get_clusters(db: Session = Depends(get_db)):
    clusters = db.query(models.Cluster).all()
    return clusters


@router.get(
    "/{name}",
    summary="Get Cluster kubeconfig by its name",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
)
async def get_kubeconfig(name: str, db: Session = Depends(get_db)):
    cluster = db.query(models.Cluster).filter(models.Cluster.name == name).first()

    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Cluster {name} not found."
        )

    try:
        process = await asyncio.create_subprocess_exec(
            "kind",
            "get",
            "kubeconfig",
            "--name",
            cluster.name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        resp, _ = await process.communicate()
    except OSError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Subprocess error: {err}.",
        )

    if not resp:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail=f"Cluster {name} not ready yet. Try again later.",
        )

    kubeconfig = yaml.safe_load(resp)

    return kubeconfig


@router.post(
    "/",
    summary="Create Cluster",
    response_description="Return HTTP Status Code 200 (CREATED)",
    status_code=status.HTTP_201_CREATED,
    response_model=models.ClusterSchema,
)
async def create_cluster(
    payload: models.ClusterSchemaCreate, db: Session = Depends(get_db)
):
    count = db.query(models.Cluster).count()
    if count >= settings.KAAS_MAX_CLUSTERS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"The KaaS service has reached its cluster limit, which is set at {settings.KAAS_MAX_CLUSTERS}. "
            "Please attempt again later or, if you wish to proceed immediately, consider listing and "
            "deleting an existing cluster.",
        )

    cluster = models.Cluster(**payload.model_dump())
    cluster.status = models.ClusterStatus.provisioning
    try:
        db.add(cluster)
        db.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cluster {payload.name} already exists.",
        )

    try:
        await asyncio.create_subprocess_exec(
            "kind",
            "create",
            "cluster",
            "--image",
            settings.KAAS_IMAGE,
            "--config",
            settings.KAAS_CONFIG,
            "--name",
            payload.name,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
    except OSError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Subprocess error: {err}.",
        )

    return cluster


@router.delete(
    "/",
    summary="Delete Cluster",
    response_description="Return HTTP Status Code 200 (DELETED)",
    status_code=status.HTTP_200_OK,
    response_model=models.OKSchema,
)
async def delete_cluster(name: str, db: Session = Depends(get_db)):
    cluster_query = db.query(models.Cluster).filter(models.Cluster.name == name)

    cluster = cluster_query.first()
    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Cluster {name} not found."
        )

    try:
        await asyncio.create_subprocess_exec(
            "kind",
            "delete",
            "cluster",
            "--name",
            name,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await asyncio.create_subprocess_exec(
            "kubectl",
            "--kubeconfig",
            settings.OBSERVER_KUBECONFIG,
            "patch",
            "cm",
            "kaas-clusters",
            "-p",
            f'{{"data":{{"{name}":null}}}}',
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
    except OSError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Subprocess error: {err}.",
        )

    cluster_query.delete(synchronize_session=False)
    db.commit()

    logger.info(f"The deletion of the cluster {name} is done.")
    return models.OKSchema(status="DELETED")
