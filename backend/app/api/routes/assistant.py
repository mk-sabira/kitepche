import logging
from typing import Literal

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.services.assistant import ask_assistant
from app.api.deps import get_current_user
from app.models.user import User
from app.core.rate_limit import RateLimiter

logger = logging.getLogger(__name__)

router = APIRouter()


assistant_limiter = RateLimiter(max_requests=10, window_seconds=60 * 60)

class AssistantRequest(BaseModel):
    text: str = Field(min_length=1)
    question: str = Field(min_length=1)
    language: Literal["ky", "ru", "en"] = "en"


class AssistantResponse(BaseModel):
    answer: str
    tools_used: list[str]


@router.post("/assistant", response_model=AssistantResponse)
def assistant(
    request: AssistantRequest,
    current_user: User = Depends(get_current_user),
    ):
    if not request.text.strip() or not request.question.strip():
        raise HTTPException(status_code=400, detail="Text and question must not be empty")
    
    wait = assistant_limiter.check(current_user.id)
    if wait is not None:
        raise HTTPException(
            status_code=429,
            detail="Too many questions. Please try again later.",
            headers={"Retry-After": str(wait)},
        )
    
    try:
        return ask_assistant(request.text, request.question, request.language)
    except Exception:
        logger.exception("Assistant call failed")
        raise HTTPException(status_code=502, detail="The assistant is unavailable, please try again")