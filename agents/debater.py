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

    brevity = "Keep it brief — 2 to 3 sentences only. " if short else ""

    if round_num == 1 and not history:
        prompt = (
            f"The debate topic is: **{topic}**\n\n"
            f"{brevity}You are opening the debate. State your position clearly and give a concrete reason for it. "
            "Speak naturally, like you would in a real high-stakes discussion. Finish every sentence completely."
        )
    elif round_num == 1:
        last = history[-1]
        prompt = (
            f"The debate topic is: **{topic}**\n\n"
            f"{brevity}Respond directly to what {last.persona_name} just said. "
            "Challenge or build on their point, then clearly state your own position with a specific reason. "
            "Speak naturally and finish every thought completely."
            f"{context_block}"
        )
    else:
        last = history[-1]
        prompt = (
            f"The debate topic is: **{topic}**\n\n"
            f"Round {round_num} — {brevity}Push back on {last.persona_name}'s argument. "
            "Name what they got wrong or what they're ignoring, then reinforce your own stance with a clear reason. "
            "Speak naturally, as a real person would. Complete every sentence — do not trail off."
            f"{context_block}"
        )

    stream = await _client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=120 if short else 400,
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
