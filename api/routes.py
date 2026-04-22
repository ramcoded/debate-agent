from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from core.orchestrator import run_debate

router = APIRouter()


@router.get("/debate")
async def debate_stream(
    topic: str = Query(..., min_length=5, max_length=300),
    num_rounds: int = Query(default=2, ge=1, le=3),
):
    return StreamingResponse(
        run_debate(topic, num_rounds),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
