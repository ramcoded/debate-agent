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

    if round_num == 1:
        prompt = (
            f"The debate topic is: **{topic}**\n\n"
            f"{brevity}Present your opening argument. Be direct, specific, and establish your position immediately."
            f"{context_block}"
        )
    else:
        prompt = (
            f"The debate topic is: **{topic}**\n\n"
            f"Round {round_num} — {brevity}Respond to the arguments made so far. "
            "Address specific points made by other debaters by name. "
            "Advance your position, challenge theirs, and sharpen your argument."
            f"{context_block}"
        )

    stream = await _client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=120 if short else 350,
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
