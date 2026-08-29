import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_MODEL_NAME: str
    AZURE_OPENAI_API_VERSION: str
    AZURE_OPENAI_API_ENDPOINT: str

    AZURE_OPENAI_EMBEDDING_API_KEY: str
    AZURE_OPENAI_EMBEDDING_API_VERSION: str
    AZURE_OPENAI_EMBEDDING_API_ENDPOINT: str
    AZURE_OPENAI_EMBEDDING_API_DEPLOYMENT: str
    AZURE_OPENAI_EMBEDDING_MODEL_NAME: str

    APP_HOST: str
    APP_PORT: int

    LANGSMITH_TRACING: bool = False
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "aria"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "allow"}


settings = Settings()


if settings.LANGSMITH_TRACING:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT