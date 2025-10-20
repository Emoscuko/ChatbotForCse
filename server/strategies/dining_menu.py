from __future__ import annotations
from .base import Strategy, StrategyContext
from ..clients.akdeniz import get_menu_for
from ..utils.dates import today_ist, tomorrow_ist, format_date_tr

class DiningMenuStrategy(Strategy):
    name = 'dining_menu'

    async def handle(self, ctx: StrategyContext, intent: dict) -> str:
        rel = intent.get('date_rel', 'today')  # 'today' | 'tomorrow'
        d = today_ist() if rel == 'today' else tomorrow_ist()
        menu = await get_menu_for(d)
        lines = '\n'.join(f'- {item}' for item in menu['items'])
        return f"**Yemekhane Menüsü — {format_date_tr(d)}**\n{lines}"