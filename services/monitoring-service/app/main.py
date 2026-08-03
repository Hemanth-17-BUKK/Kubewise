from fastapi import FastAPI

from app.api.monitoring import router as monitoring_router

app = FastAPI(
    title="Monitoring Service",
    version="1.0.0"
)

app.include_router(monitoring_router)


@app.get("/")
def health():
    return {
        "service": "Monitoring Service",
        "status": "running"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}