from fastapi import APIRouter

from app.models.request import AnalyzeRequest
from app.services.analysis_service import AnalysisService

router = APIRouter()

analysis_service = AnalysisService()


@router.post("/analyze")
async def analyze(request: AnalyzeRequest):
    return await analysis_service.analyze(request)