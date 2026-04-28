from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse
from core.orchestrator import run_debate
from api.security import limiter, sanitize_topic

router = APIRouter()


@router.get("/debate")
@limiter.limit("5/minute")
async def debate_stream(
    request: Request,
    topic: str = Query(..., min_length=5, max_length=300),
    num_rounds: int = Query(default=2, ge=1, le=3),
    num_agents: int = Query(default=4),
    short: bool = Query(default=False),
):
    if num_agents not in (2, 4):
        num_agents = 4
    clean_topic = sanitize_topic(topic)
    return StreamingResponse(
        run_debate(clean_topic, num_rounds, short, num_agents),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
