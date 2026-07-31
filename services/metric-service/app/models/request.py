from pydantic import BaseModel, Field


class PrometheusRequest(BaseModel):
    cluster_name: str = Field(alias="clusterName")
    role_arn: str = Field(alias="roleArn")

    model_config = {
        "populate_by_name": True
    }