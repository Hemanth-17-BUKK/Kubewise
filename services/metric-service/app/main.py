from fastapi import FastAPI

from app.api.metrics import router as metrics_router

app = FastAPI(
    title="Metric Service",
    version="1.0.0"
)

app.include_router(metrics_router)


@app.get("/")
def root():
    return {
        "service": "Metric Service",
        "status": "running"
    }