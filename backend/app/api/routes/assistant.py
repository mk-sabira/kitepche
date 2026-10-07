import logging
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.assistant import ask_assistant

logger = logging.getLogger(__name__)

router = APIRouter()



class AssistantRequest(BaseModel):
    text: str = Field(min_length=1)
    question: str = Field(min_length=1)
    language: Literal["ky", "ru", "en"] = "en"


class AssistantResponse(BaseModel):
    answer: str
    tools_used: list[str]


@router.post("/assistant", response_model=AssistantResponse)
def assistant(request: AssistantRequest):
    if not request.text.strip() or not request.question.strip():
        raise HTTPException(status_code=400, detail="Text and question must not be empty")

    try:
        return ask_assistant(request.text, request.question, request.language)
    except Exception:
        logger.exception("Assistant call failed")
        raise HTTPException(status_code=502, detail="The assistant is unavailable, please try again")