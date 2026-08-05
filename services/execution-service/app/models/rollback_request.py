from pydantic import BaseModel


class RollbackRequest(BaseModel):

    cluster_name: str

    target_node_count: int