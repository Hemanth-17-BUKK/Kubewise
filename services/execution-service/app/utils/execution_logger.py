from datetime import datetime


class ExecutionLogger:

    def __init__(self):

        self.logs = []

    def add(
        self,
        step,
        status,
        message
    ):

        self.logs.append({

            "timestamp": datetime.utcnow().isoformat(),

            "step": step,

            "status": status,

            "message": message

        })

    def get_logs(self):

        return self.logs