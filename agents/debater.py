import anthropic
from core.models import Persona, DebateMessage
from typing import AsyncGenerator

_client = anthropic.AsyncAnthropic()


async def stream_argument(
    persona: Persona,
    topic: str,
    round_num: int,
    history: list[DebateMessage],
) -> AsyncGenerator[str, None]:
    context_block = ""
    if history:
        lines = []
        for msg in history:
            lines.append(f"**{msg.persona_name} — {msg.persona_role}** (Round {msg.round}):\n{msg.content}")
        context_block = "\n\n---\n\nArguments so far:\n\n" + "\n\n".join(lines)

    if round_num == 1:
        prompt = (
            f"The debate topic is: **{topic}**\n\n"
            "Present your opening argument. Be direct, specific, and establish your position immediately."
            f"{context_block}"
        )
    else:
        prompt = (
            f"The debate topic is: **{topic}**\n\n"
            f"Round {round_num} — Respond to the arguments made so far. "
            "Address specific points made by other debaters by name. "
            "Advance your position, challenge theirs, and sharpen your argument."
            f"{context_block}"
        )

    async with _client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=350,
        system=persona.system_prompt,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        async for token in stream.text_stream:
            yield token
