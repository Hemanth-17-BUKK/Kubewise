from fastapi import APIRouter, HTTPException

from app.repositories.execution_repository import ExecutionRepository

router = APIRouter(
    prefix="/executions",
    tags=["Execution History"]
)


@router.get("")
def get_all():

    return ExecutionRepository.all()


@router.get("/{operation_id}")
def get_by_id(operation_id: str):

    execution = ExecutionRepository.get(operation_id)

    if execution is None:

        raise HTTPException(
            status_code=404,
            detail="Execution not found."
        )

    return execution