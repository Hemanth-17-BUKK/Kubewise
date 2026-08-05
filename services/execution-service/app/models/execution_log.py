from datetime import datetime
from pydantic import BaseModel


class ExecutionLog(BaseModel):

    timestamp: datetime

    step: str

    status: str

    message: str