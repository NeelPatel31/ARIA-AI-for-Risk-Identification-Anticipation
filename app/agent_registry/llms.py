from langchain_openai import AzureChatOpenAI

from app.config import settings


llm = AzureChatOpenAI(
    api_key=settings.AZURE_OPENAI_API_KEY, 
    model=settings.AZURE_OPENAI_MODEL_NAME, 
    api_version=settings.AZURE_OPENAI_API_VERSION, 
    azure_endpoint=settings.AZURE_OPENAI_API_ENDPOINT,
    temperature=0.1
)