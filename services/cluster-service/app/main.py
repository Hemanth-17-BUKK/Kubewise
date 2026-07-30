from fastapi import FastAPI

from app.api.aws import router as aws_router

app = FastAPI(
    title="KubeWise Cluster Service",
    version="1.0.0"
)

app.include_router(aws_router)


@app.get("/health")
def health():

    return {
        "status": "UP",
        "service": "cluster-service"
    }