from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # -------------------------------------------------
    # Application
    # -------------------------------------------------

    app_name: str = "KubeWise Metric Service"

    # -------------------------------------------------
    # AWS
    # -------------------------------------------------

    aws_region: str = "us-east-1"

    role_session_name: str = "kubewise-session"

    # -------------------------------------------------
    # Prometheus
    # -------------------------------------------------

    prometheus_url: str = "http://localhost:9090"

    class Config:
        env_file = ".env"


settings = Settings()