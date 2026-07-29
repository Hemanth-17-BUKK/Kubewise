from fastapi import APIRouter

from app.schemas.connect import ClusterConnectRequest
from app.schemas.response import ClusterConnectResponse
from app.services.monitoring_service import MonitoringService

router = APIRouter(prefix="/api/v1/clusters", tags=["Monitoring"])

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