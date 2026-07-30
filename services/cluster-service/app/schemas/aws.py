from pydantic import BaseModel


class AWSConnectRequest(BaseModel):
    roleArn: str


class ClusterInfo(BaseModel):
    name: str
    arn: str
    region: str
    status: str
    version: str


class AWSConnectResponse(BaseModel):
    connectionId: str
    accountId: str
    clusters: list[ClusterInfo]