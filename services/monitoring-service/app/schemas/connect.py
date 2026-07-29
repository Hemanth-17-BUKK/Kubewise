from pydantic import BaseModel


class ClusterConnectRequest(BaseModel):
    roleArn: str
    clusterName: str