from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str

    METRIC_SERVICE_URL: str

    AWS_REGION: str
    BEDROCK_MODEL_ID: str

    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()