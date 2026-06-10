import logging
from uuid import uuid4

from fastapi import APIRouter

from app.agent import build_agent
from app.schemas import AskRequest, AskResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
async def ask(body: AskRequest) -> AskResponse:
    sid = body.session_id or str(uuid4())
    logger.info("request session_id=%s question=%r", sid, body.question)
    agent = build_agent(sid)
    result = agent(body.question)
    return AskResponse(answer=str(result), session_id=sid)
