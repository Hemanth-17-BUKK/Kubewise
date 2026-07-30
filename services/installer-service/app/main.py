from fastapi import FastAPI

from app.api.prometheus import router as prometheus_router

app = FastAPI(title="Kubewise Installer Service")

app.include_router(prometheus_router)


@app.get("/health")
def health():
    return {"status": "healthy"}