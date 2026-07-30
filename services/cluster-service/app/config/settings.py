from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    app_name: str = "KubeWise Cluster Service"

    aws_region: str = "us-east-1"

    role_session_name: str = "kubewise-session"

    class Config:
        env_file = ".env"


settings = Settings()