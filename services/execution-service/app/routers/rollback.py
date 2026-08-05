from fastapi import APIRouter

from app.models.rollback_request import RollbackRequest
from app.services.rollback_service import RollbackService

router = APIRouter(
    prefix="/rollback",
    tags=["Rollback"]
)

service = RollbackService()


@router.post("")
async def rollback(request: RollbackRequest):

    return await service.rollback(request)