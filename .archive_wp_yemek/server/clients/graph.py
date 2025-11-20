from __future__ import annotations
import os
import httpx
from typing import Iterable, Optional

GRAPH_BASE = 'https://graph.microsoft.com/v1.0'
AZURE_TENANT_ID = os.getenv('AZURE_TENANT_ID')
AZURE_CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
AZURE_CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')

class GraphAuthError(RuntimeError):
    pass

async def _get_token(client: httpx.AsyncClient) -> str:
    if not (AZURE_TENANT_ID and AZURE_CLIENT_ID and AZURE_CLIENT_SECRET):
        raise GraphAuthError('Graph creds missing: set AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET')
    token_url = f'https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/token'
    data = {
        'client_id': AZURE_CLIENT_ID,
        'client_secret': AZURE_CLIENT_SECRET,
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials',
    }
    r = await client.post(token_url, data=data, timeout=10)
    r.raise_for_status()
    return r.json()['access_token']

async def fetch_channel_messages(team_id: str, channel_id: str, top: int = 30) -> list[dict]:
    async with httpx.AsyncClient() as client:
        token = await _get_token(client)
        url = f'{GRAPH_BASE}/teams/{team_id}/channels/{channel_id}/messages?$top={top}'
        r = await client.get(url, headers={'Authorization': f'Bearer {token}'}, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get('value', [])

# Helper to plaintext message content (Graph returns HTML-like content)
from bs4 import BeautifulSoup

def msg_html_to_text(content_html: str) -> str:
    try:
        return BeautifulSoup(content_html or '', 'html.parser').get_text('\n').strip()
    except Exception:
        return content_html or ''