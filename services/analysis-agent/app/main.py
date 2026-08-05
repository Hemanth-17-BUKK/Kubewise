from fastapi import FastAPI

from app.config import settings
from app.routers.analyze import router as analyze_router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

# Register routers AFTER app is created
app.include_router(analyze_router)


@app.get("/")
def root():
    return {
        "message": "Analysis Agent"
    }


@app.get("/health")
def health():
    return {
        "status": "UP",
        "service": "analysis-agent"
    }