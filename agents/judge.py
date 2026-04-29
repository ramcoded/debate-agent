from groq import AsyncGroq
from core.models import DebateMessage
from typing import AsyncGenerator

_client = AsyncGroq()

_JUDGE_SYSTEM = (
    "You are an impartial Judge delivering a concise verdict on a debate. "
    "In 2-3 short paragraphs: name the strongest argument and why it won, "
    "identify one key tension that remains unresolved, "
    "and deliver a clear decisive conclusion — no 'all sides have merit' hedging. "
    "Be direct and brief."
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
        max_tokens=280,
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
