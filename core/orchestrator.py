import json
from typing import AsyncGenerator
from core.models import EventType, DebateMessage
from agents.personas import PERSONAS
from agents.debater import stream_argument
from agents.judge import stream_verdict


def _sse(event_type: EventType, data: dict) -> str:
    payload = json.dumps({"type": event_type.value, **data})
    return f"data: {payload}\n\n"


async def run_debate(topic: str, num_rounds: int = 2, short: bool = False, num_agents: int = 4) -> AsyncGenerator[str, None]:
    try:
        active_personas = PERSONAS[:2] if num_agents == 2 else PERSONAS
        personas_meta = [
            {"id": p.id, "name": p.name, "role": p.role, "color": p.color, "emoji": p.emoji}
            for p in active_personas
        ]
        yield _sse(EventType.DEBATE_START, {"topic": topic, "num_rounds": num_rounds, "personas": personas_meta})

        history: list[DebateMessage] = []

        for round_num in range(1, num_rounds + 1):
            yield _sse(EventType.ROUND_START, {"round": round_num, "total_rounds": num_rounds})

            for persona in active_personas:
                yield _sse(EventType.AGENT_START, {
                    "persona_id": persona.id,
                    "persona_name": persona.name,
                    "persona_role": persona.role,
                    "persona_color": persona.color,
                    "persona_emoji": persona.emoji,
                    "round": round_num,
                })

                full_text = ""
                async for token in stream_argument(persona, topic, round_num, history, short=short):
                    full_text += token
                    yield _sse(EventType.AGENT_TOKEN, {"persona_id": persona.id, "token": token})

                history.append(DebateMessage(
                    persona_id=persona.id,
                    persona_name=persona.name,
                    persona_role=persona.role,
                    round=round_num,
                    content=full_text,
                ))
                yield _sse(EventType.AGENT_END, {"persona_id": persona.id})

            yield _sse(EventType.ROUND_END, {"round": round_num})

        yield _sse(EventType.JUDGE_START, {})

        full_verdict = ""
        async for token in stream_verdict(topic, history):
            full_verdict += token
            yield _sse(EventType.JUDGE_TOKEN, {"token": token})

        yield _sse(EventType.JUDGE_END, {})
        yield _sse(EventType.DEBATE_END, {"total_arguments": len(history)})

    except Exception as e:
        # Avoid leaking internal error details (API keys, stack traces) to the client
        import logging
        logging.getLogger(__name__).error("Debate error: %s", e, exc_info=True)
        yield _sse(EventType.ERROR, {"message": "An internal error occurred. Please try again."})
