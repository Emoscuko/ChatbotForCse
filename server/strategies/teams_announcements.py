from __future__ import annotations
import json
import os
import re
from typing import Dict
from .base import Strategy, StrategyContext
from ..clients.graph import fetch_channel_messages, msg_html_to_text
from ..utils.dates import format_date_tr

# Load course → (team_id, channel_id) mapping
# Example of config/courses.json:
# {
#   "Algoritma": { "team_id": "<GUID>", "channel_id": "<GUID>" },
#   "Algorithm": { "team_id": "<GUID>", "channel_id": "<GUID>" }
# }

COURSE_MAP_PATH = os.getenv('COURSE_MAP_PATH', os.path.join(os.path.dirname(__file__), '../../config/courses.json'))

try:
    with open(COURSE_MAP_PATH, 'r', encoding='utf-8') as f:
        COURSE_MAP: Dict[str, Dict[str, str]] = json.load(f)
except Exception:
    COURSE_MAP = {}

class TeamsAnnouncementsStrategy(Strategy):
    name = 'teams_announcements'

    async def handle(self, ctx: StrategyContext, intent: dict) -> str:
        course = intent.get('course')
        target_date = intent.get('date')
        course_key = _resolve_course_key(course)
        if not course_key:
            return 'Hangi ders için kontrol etmemi istersin? (Örn: Algoritma, Veri Yapıları)'

        cfg = COURSE_MAP.get(course_key)
        if not cfg:
            return f'"{course_key}" dersi için Teams kanal bilgisini bulamadım. `config/courses.json` dosyasına ekleyebilirsin.'

        try:
            msgs = await fetch_channel_messages(cfg['team_id'], cfg['channel_id'], top=40)
        except Exception as e:
            return f'Teams erişiminde sorun var: {e}'

        # Scan most-recent-first for a relevant announcement
        keywords = _keywords_for(target_date)
        best = None
        for m in msgs:
            content = msg_html_to_text(m.get('body', {}).get('content', ''))
            if any(kw.lower() in content.lower() for kw in keywords):
                best = (m, content)
                break

        if not best:
            when = format_date_tr(target_date) if target_date else 'ilgili tarih'
            return f'Teams kanalında {course_key} için {when} ile ilgili bir duyuru bulamadım. Hocanın paylaşımlarını tekrar kontrol edebilirim ya da netleştirmek için hoca/öğrenci temsilcisine yazabilirsin.'

        m, content = best
        author = (m.get('from', {}) or {}).get('user', {}).get('displayName', 'hocanız')
        created = m.get('createdDateTime', '')[:19].replace('T', ' ')
        return (
            f'• **{course_key}** için en alakalı Teams duyurusu ({author}, {created}):\n\n'
            f'{content}\n\n'
            'İstersen daha eski duyurulara da bakabilirim.'
        )


def _resolve_course_key(raw: str | None) -> str | None:
    if not raw:
        return None
    raw = raw.strip().lower()
    for key in COURSE_MAP.keys():
        if key.lower() == raw:
            return key
    # try simple aliasing
    aliases = {
        'algoritma': 'Algoritma',
        'algorithm': 'Algorithm',
        'algo': 'Algoritma',
    }
    return aliases.get(raw)


def _keywords_for(d) -> list[str]:
    kws = ['duyuru', 'ders', 'sınav', 'quiz', 'lab']
    if d is not None:
        # add language variants for relative date
        kws += ['yarın', 'yarin']
    return kws