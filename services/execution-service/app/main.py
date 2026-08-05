from fastapi import FastAPI
from app.routers.execute import router
from app.routers.history import router as history_router
from app.routers.rollback import router as rollback_router


app = FastAPI()

app.include_router(router)
app.include_router(history_router)
app.include_router(rollback_router)


@app.get("/")
def root():
    return {
        "message": "Execution Service"
    }


@app.get("/health")
def health():
    return {
        "status": "UP",
        "service": "execution-service"
    }