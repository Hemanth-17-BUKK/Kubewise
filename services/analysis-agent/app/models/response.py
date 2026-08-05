from pydantic import BaseModel


class AnalysisResponse(BaseModel):
    report: dict
    optimization_plan: dict