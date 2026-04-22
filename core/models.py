from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class EventType(str, Enum):
    DEBATE_START = "debate_start"
    ROUND_START = "round_start"
    AGENT_START = "agent_start"
    AGENT_TOKEN = "agent_token"
    AGENT_END = "agent_end"
    ROUND_END = "round_end"
    JUDGE_START = "judge_start"
    JUDGE_TOKEN = "judge_token"
    JUDGE_END = "judge_end"
    DEBATE_END = "debate_end"
    ERROR = "error"


class Persona(BaseModel):
    id: str
    name: str
    role: str
    description: str
    color: str
    emoji: str
    system_prompt: str


class DebateMessage(BaseModel):
    persona_id: str
    persona_name: str
    persona_role: str
    round: int
    content: str


class DebateRequest(BaseModel):
    topic: str
    num_rounds: int = 2
