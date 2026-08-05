from pydantic import BaseModel, Field

class ExecuteRequest(BaseModel):
    cluster_name: str
    role_arn: str
    target_node_count: int
    approval: bool
    dry_run: bool = Field(default=False)