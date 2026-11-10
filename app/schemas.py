# Se definen los contratos de entrada y salida de nuestra API mediante Pydantic

from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    user_id: str = Field(min_length=1)


class ChatResponse(BaseModel):
    answer: str
    agents_used: list[str]
    sources: list[str]
    status: Literal[
        "success",
        "insufficient_information",
        "pending_human_review",
        "error",
    ]
