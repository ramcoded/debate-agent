from groq import AsyncGroq
from core.models import Persona, DebateMessage
from typing import AsyncGenerator

_client = AsyncGroq()


async def stream_argument(
    persona: Persona,
    topic: str,
    round_num: int,
    history: list[DebateMessage],
    short: bool = False,
) -> AsyncGenerator[str, None]:
    context_block = ""
    if history:
        lines = []
        for msg in history:
            lines.append(f"**{msg.persona_name} — {msg.persona_role}** (Round {msg.round}):\n{msg.content}")
        context_block = "\n\n---\n\nArguments so far:\n\n" + "\n\n".join(lines)

    brevity = "Be concise — 2 to 3 sentences maximum. " if short else ""

    if round_num == 1 and not history:
        prompt = (
            f"The debate topic is: **{topic}**\n\n"
            f"{brevity}You are opening the debate. Present your position directly and establish your stance immediately."
        )
    elif round_num == 1:
        last = history[-1]
        prompt = (
            f"The debate topic is: **{topic}**\n\n"
            f"{brevity}{last.persona_name} just argued their position. "
            "Respond directly to their argument, then state your own case clearly."
            f"{context_block}"
        )
    else:
        last = history[-1]
        prompt = (
            f"The debate topic is: **{topic}**\n\n"
            f"Round {round_num} — {brevity}Address {last.persona_name}'s most recent argument directly. "
            "Push back on their specific claims, then sharpen your own position."
            f"{context_block}"
        )

    stream = await _client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=50 if short else 90,
        messages=[
            {"role": "system", "content": persona.system_prompt},
            {"role": "user", "content": prompt},
        ],
        stream=True,
    )
    async for chunk in stream:
        token = chunk.choices[0].delta.content
        if token:
            yield token
