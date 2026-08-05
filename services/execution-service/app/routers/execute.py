from fastapi import APIRouter

from app.models.request import ExecuteRequest
from app.services.execution_service import ExecutionService

router = APIRouter()

execution_service = ExecutionService()


@router.post("/execute")
async def execute(request: ExecuteRequest):
    return await execution_service.execute(request)