from fastapi import APIRouter

from app.schemas.connect import ClusterConnectRequest
from app.schemas.response import ClusterConnectResponse
from app.services.monitoring_service import MonitoringService

router = APIRouter(
    prefix="/api/v1/clusters",
    tags=["Monitoring"],
)

service = MonitoringService()


@router.post(
    "/connect",
    response_model=ClusterConnectResponse,
)
def connect(request: ClusterConnectRequest):
    return service.connect(
        request.roleArn,
        request.clusterName,
    )


@router.post("/namespaces")
def namespaces(request: ClusterConnectRequest):
    return service.list_namespaces(
        request.roleArn,
        request.clusterName,
    )


@router.post("/nodes")
def nodes(request: ClusterConnectRequest):
    return service.list_nodes(
        request.roleArn,
        request.clusterName,
    )


@router.post("/pods")
def pods(request: ClusterConnectRequest):
    return service.list_pods(
        request.roleArn,
        request.clusterName,
    )


@router.post("/deployments")
def deployments(request: ClusterConnectRequest):
    return service.list_deployments(
        request.roleArn,
        request.clusterName,
    )


@router.post("/services")
def services(request: ClusterConnectRequest):
    return service.list_services(
        request.roleArn,
        request.clusterName,
    )


@router.post("/node-metrics")
def node_metrics(request: ClusterConnectRequest):
    return service.get_node_metrics(
        request.roleArn,
        request.clusterName,
    )


@router.post("/pod-metrics")
def pod_metrics(request: ClusterConnectRequest):
    return service.get_pod_metrics(
        request.roleArn,
        request.clusterName,
    )