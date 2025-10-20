from __future__ import annotations
from typing import Optional
from .strategies.base import StrategyContext
from .strategies.teams_announcements import TeamsAnnouncementsStrategy
from .strategies.dining_menu import DiningMenuStrategy
from .strategies.fallback import FallbackStrategy
from .nlp import detect_intent

class StrategyRouter:
    def __init__(self):
        self.teams = TeamsAnnouncementsStrategy()
        self.menu = DiningMenuStrategy()
        self.fallback = FallbackStrategy()

    async def route(self, text: str, user: Optional[str], chat_id: Optional[str], is_group: bool) -> str:
        ctx = StrategyContext(text=text, user=user, chat_id=chat_id, is_group=is_group)
        intent = detect_intent(text)
        name = intent.get('name')
        if name == 'teams_announcements':
            return await self.teams.handle(ctx, intent)
        if name == 'dining_menu':
            return await self.menu.handle(ctx, intent)
        return await self.fallback.handle(ctx, intent)