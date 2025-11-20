import 'dotenv/config';
import wppconnect from '@wppconnect-team/wppconnect';

const PY_AI_URL = process.env.PY_AI_URL || 'http://127.0.0.1:8000';
const SHARED_SECRET = process.env.SHARED_SECRET || 'hello';
const TRIGGER_PREFIX = process.env.TRIGGER_PREFIX ?? '!ask';

// Don't log secrets in prod
console.log('Bridge starting with prefix:', TRIGGER_PREFIX || '(none: answer everything)');

wppconnect.create().then(start).catch(console.error);

function shouldAnswer(body) {
  if (!body) return false;
  if (!TRIGGER_PREFIX) return true;            // empty => answer everything
  return body.trim().toLowerCase().startsWith(TRIGGER_PREFIX.toLowerCase());
}

async function askPython(prompt, ctx) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 20000); // 20s timeout
  try {
    const res = await fetch(`${PY_AI_URL}/answer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Auth': SHARED_SECRET,
      },
      body: JSON.stringify({
        text: prompt,
        user: ctx.user,
        chat_id: ctx.chatId,
        is_group: ctx.isGroup,
      }),
      signal: controller.signal,
    });
    clearTimeout(timer);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return (data.answer || '').toString().trim();
  } catch (e) {
    clearTimeout(timer);
    console.error('Python bridge error:', e.message);
    return 'AI servisine ulaşamadım. Birazdan tekrar dene.';
  }
}

async function start(client) {
  console.log('✅ WhatsApp ↔ Python (Strategy Router) is live.');

  client.onMessage(async (message) => {
    const body = (message.body || '').trim();
    if (!body) return;

    if (!shouldAnswer(body)) return;

    // strip trigger if present (case-insensitive)
    const regex = new RegExp(`^${TRIGGER_PREFIX.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s*`, 'i');
    const prompt = TRIGGER_PREFIX ? body.replace(regex, '') : body;

    const ctx = {
      user: message.sender?.pushname || message.sender?.shortName || message.from,
      chatId: message.chatId,
      isGroup: !!message.isGroupMsg,
    };

    console.log(`📩 ${ctx.isGroup ? '[GROUP]' : '[DM]'} ${ctx.user}: ${prompt}`);

    const answer = await askPython(prompt, ctx);

    const to = message.chatId || message.from;
    await client.sendText(to, answer);
  });
}