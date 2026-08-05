from pydantic import BaseModel


class ExecuteResponse(BaseModel):
    status: str
    operation_id: str
    removed_node: str
    nodes_before: int
    nodes_after: int
    pods_evicted: int
    execution_time_seconds: int
    cluster_healthy: bool