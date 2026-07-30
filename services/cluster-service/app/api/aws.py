from fastapi import APIRouter

from app.schemas.aws import (
    AWSConnectRequest,
    AWSConnectResponse,
)

from app.services.aws_service import AWSService


router = APIRouter(
    prefix="/api/v1/aws",
    tags=["AWS"],
)

service = AWSService()


@router.post(
    "/connect",
    response_model=AWSConnectResponse
)
def connect(request: AWSConnectRequest):

    return service.connect(request.roleArn)