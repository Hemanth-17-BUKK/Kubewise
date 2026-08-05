from datetime import datetime


class ExecutionRepository:

    history = []

    # ----------------------------------------
    # Save Execution
    # ----------------------------------------

    @classmethod
    def save(cls, execution):

        cls.history.append(execution)

    # ----------------------------------------
    # Get All Executions
    # ----------------------------------------

    @classmethod
    def all(cls):

        return cls.history

    # ----------------------------------------
    # Get Single Execution
    # ----------------------------------------

    @classmethod
    def get(cls, operation_id):

        for execution in cls.history:

            if execution["operation_id"] == operation_id:

                return execution

        return None

    # ----------------------------------------
    # Update Execution Status
    # ----------------------------------------

    @classmethod
    def update_status(
        cls,
        operation_id,
        status,
        message=None
    ):

        execution = cls.get(operation_id)

        if execution is None:
            return

        execution["status"] = status

        if "response" in execution:
            execution["response"]["status"] = status

            if message is not None:
                execution["response"]["message"] = message

        if status in [
            "COMPLETED",
            "FAILED",
            "ROLLED_BACK"
        ]:
            execution["completed_at"] = datetime.utcnow().isoformat()

    # ----------------------------------------
    # Update Execution Response
    # ----------------------------------------

    @classmethod
    def update_response(
        cls,
        operation_id,
        response
    ):

        execution = cls.get(operation_id)

        if execution is None:
            return

        execution["response"] = response

        if "status" in response:
            execution["status"] = response["status"]

        if execution["status"] in [
            "COMPLETED",
            "FAILED",
            "ROLLED_BACK"
        ]:
            execution["completed_at"] = datetime.utcnow().isoformat()

    # ----------------------------------------
    # Add Log Entry
    # ----------------------------------------

    @classmethod
    def add_log(
        cls,
        operation_id,
        log
    ):

        execution = cls.get(operation_id)

        if execution is None:
            return

        execution.setdefault("logs", []).append(log)