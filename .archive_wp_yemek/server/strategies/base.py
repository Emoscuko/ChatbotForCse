from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class StrategyContext:
    text: str
    user: Optional[str]
    chat_id: Optional[str]
    is_group: bool

class Strategy(ABC):
    name: str = 'base'

    @abstractmethod
    async def handle(self, ctx: StrategyContext, intent: dict) -> str:
        ...