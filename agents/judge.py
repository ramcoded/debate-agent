from groq import AsyncGroq
from core.models import DebateMessage
from typing import AsyncGenerator

_client = AsyncGroq()

_JUDGE_SYSTEM = (
    "You are an impartial, intellectually rigorous Judge presiding over a multi-expert debate. "
    "Your verdict must: (1) identify which arguments were strongest and why, "
    "(2) name specific points of consensus that emerged, "
    "(3) name the key unresolved tensions, "
    "(4) deliver a clear, actionable synthesis — not a wishy-washy 'all sides have merit' non-answer. "
    "Structure your verdict with clear sections. Be decisive. Write 4-5 paragraphs."
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
        max_tokens=700,
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
