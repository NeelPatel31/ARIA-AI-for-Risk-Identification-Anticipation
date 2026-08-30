from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    user_query: str = Field(..., description="The user query to retrieve/answer against the product data")


class StreamChatRequest(BaseModel):
    session_id: str = Field(..., description="Conversation/session thread id for the agent checkpointer")
    user_query: str = Field(..., description="The user message to send to the agent")
