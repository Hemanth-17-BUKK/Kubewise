from typing import List

from pydantic import BaseModel


class ClusterConnectResponse(BaseModel):
    connected: bool
    cluster: str
    namespaces: List[str]