from fastapi import APIRouter, HTTPException, Query
from app.services.metric_service import MetricService

router = APIRouter(prefix="/metrics", tags=["Metrics"])

metric_service = MetricService()


# ----------------------------------------------------
# Cluster Metrics
# ----------------------------------------------------

@router.get("/cpu")
def cpu_usage():
    return metric_service.get_cpu_usage()


@router.get("/memory")
def memory_usage():
    return metric_service.get_memory_usage()


# ----------------------------------------------------
# Pod Metrics
# ----------------------------------------------------

@router.get("/pods/cpu")
def top_cpu_pods():
    return metric_service.get_top_cpu_pods()


@router.get("/pods/memory")
def top_memory_pods():
    return metric_service.get_top_memory_pods()


# ----------------------------------------------------
# Node Metrics
# ----------------------------------------------------

@router.get("/nodes/cpu")
def node_cpu_usage():
    return metric_service.get_node_cpu_usage()


@router.get("/nodes/memory")
def node_memory_usage():
    return metric_service.get_node_memory_usage()


# ----------------------------------------------------
# Dashboard Overview
# ----------------------------------------------------

@router.get("/overview")
def overview():
    return metric_service.get_overview()


# ----------------------------------------------------
# Historical Metrics
# ----------------------------------------------------

@router.get("/history/cpu")
def cpu_history(
    duration: str = Query(default="1h"),
    start: str | None = Query(default=None),
    end: str | None = Query(default=None),
    step: str | None = Query(default=None),
):
    try:
        return metric_service.get_cpu_history(
            duration=duration,
            start=start,
            end=end,
            step=step,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history/memory")
def memory_history(
    duration: str = Query(default="1h"),
    start: str | None = Query(default=None),
    end: str | None = Query(default=None),
    step: str | None = Query(default=None),
):
    try:
        return metric_service.get_memory_history(
            duration=duration,
            start=start,
            end=end,
            step=step,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))