from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    cluster_name: str
    role_arn: str