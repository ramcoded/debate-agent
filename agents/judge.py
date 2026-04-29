from groq import AsyncGroq
from core.models import DebateMessage
from typing import AsyncGenerator

_client = AsyncGroq()

_JUDGE_SYSTEM = (
    "You are an impartial Judge delivering a verdict on a debate. "
    "Write exactly one paragraph: say whose argument was strongest and why it landed, then give your decisive conclusion. "
    "Talk like a real person giving a clear-headed verdict — no hedging, no lists, no headers, no bold text, no asterisks, no symbols. "
    "Plain spoken sentences only. Stop after one paragraph."
)


async def stream_verdict(
    topic: str,
    history: list[DebateMessage],
) -> AsyncGenerator[str, None]:
    transcript = "\n\n".join(
        f"**{m.persona_name} — {m.persona_role}** (Round {m.round}):\n{m.content}"
        for m in history
    )

    prompt = (
        f"Debate topic: **{topic}**\n\n"
        f"Full transcript:\n\n{transcript}\n\n"
        "Deliver your verdict. Be decisive, specific, and name names."
    )

    stream = await _client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=180,
        messages=[
            {"role": "system", "content": _JUDGE_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        stream=True,
    )
    async for chunk in stream:
        token = chunk.choices[0].delta.content
        if token:
            yield token
