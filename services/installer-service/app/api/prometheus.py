from fastapi import APIRouter

from app.models.request import PrometheusRequest
from app.services.prometheus_service import PrometheusService

router = APIRouter(
    prefix="/api/v1/prometheus",
    tags=["Prometheus"],
)

service = PrometheusService()


@router.post("/status")
def check_status(request: PrometheusRequest):

    return service.get_prometheus_status(
        role_arn=request.role_arn,
        cluster_name=request.cluster_name,
    )

@router.post("/install")
def install_prometheus(request: PrometheusRequest):

    return service.install_prometheus(
        role_arn=request.role_arn,
        cluster_name=request.cluster_name,
    )