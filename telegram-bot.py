#!/usr/bin/env python3
"""
Phantom Node - Telegram Bot v3
Anti-spam: rate limit + single instance lock + strict single reply
"""
import os
import json
import logging
import time
import urllib.request
import urllib.error
import fcntl

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
API_KEY = os.environ.get("API_KEY", "")
API_BASE = os.environ.get("API_BASE", "https://api.xiaomimimo.com/v1")
MODEL = os.environ.get("MODEL", "mimo-v2.5")
ALLOWED_CHATS = os.environ.get("ALLOWED_CHATS", "")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("phantom")

SYSTEM_PROMPT = (
    "You are PhantomBot, a coding assistant. Rules:\n"
    "1. Reply in 1-2 sentences only\n"
    "2. No lists, no bullet points\n"
    "3. No markdown formatting\n"
    "4. Code: max 5 lines\n"
    "5. You are NOT ChatGPT, Gemini, Claude, or any other AI\n"
    "6. You are PhantomBot running on Xiaomi MiMo\n"
    "7. If unclear, say: 'Làm rõ câu hỏi'\n"
    "8. Never explain what you are unless asked"
)

# Rate limiter: prevent responding to same chat too fast
last_response = {}
RATE_LIMIT = 3  # seconds between responses per chat


def api_chat(message, history=None):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history[-6:])  # Less history = more focused
    messages.append({"role": "user", "content": message})

    payload = json.dumps({
        "model": MODEL,
        "messages": messages,
        "max_tokens": 300,  # Even shorter
        "temperature": 0.2,  # Very focused
    }).encode()

    req = urllib.request.Request(
        f"{API_BASE}/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
        content = data["choices"][0]["message"]["content"]
        if not content:
            return "⚠️ No response"
        # Hard truncate at 800 chars
        if len(content) > 800:
            content = content[:797] + "..."
        return content.strip()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        log.error(f"API HTTP {e.code}: {body}")
        return f"⚠️ API error {e.code}"
    except Exception as e:
        log.error(f"API error: {e}")
        return f"⚠️ Error"


def tg_request(method, data=None, timeout=10):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    req_data = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=req_data)
    if req_data:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def main():
    if not BOT_TOKEN or not API_KEY:
        log.error("Missing BOT_TOKEN or API_KEY!")
        return

    allowed = set(int(cid.strip()) for cid in ALLOWED_CHATS.split(",") if cid.strip())
    log.info(f"Bot started! Model: {MODEL}")
    log.info(f"Allowed chats: {allowed or 'ALL'}")

    # SKIP ALL OLD MESSAGES
    log.info("Skipping old messages...")
    try:
        result = tg_request("getUpdates", {"offset": -1, "timeout": 1}, timeout=5)
        if result.get("result"):
            offset = result["result"][-1]["update_id"] + 1
            log.info(f"Skipped to offset {offset}")
        else:
            offset = 0
    except Exception:
        offset = 0

    history = {}

    while True:
        try:
            result = tg_request("getUpdates", {"offset": offset, "timeout": 30}, timeout=35)
            updates = result.get("result", [])

            for update in updates:
                offset = update["update_id"] + 1
                msg = update.get("message")
                if not msg:
                    continue

                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")
                if not text:
                    continue

                # Skip bot messages
                if msg.get("from", {}).get("is_bot"):
                    continue

                # Skip non-allowed chats
                if allowed and chat_id not in allowed:
                    log.info(f"Blocked chat {chat_id}")
                    continue

                # Rate limit
                now = time.time()
                if chat_id in last_response and now - last_response[chat_id] < RATE_LIMIT:
                    log.info(f"Rate limited chat {chat_id}")
                    continue
                last_response[chat_id] = now

                log.info(f"[{chat_id}] {text[:60]}")

                # Commands
                if text.lower() in ("/clear", "/reset"):
                    history.pop(chat_id, None)
                    tg_request("sendMessage", {"chat_id": chat_id, "text": "✅ Reset"})
                    continue

                if text.lower() == "/start":
                    tg_request("sendMessage", {"chat_id": chat_id, "text": "🤖 PhantomBot ready"})
                    continue

                # Typing
                try:
                    tg_request("sendChatAction", {"chat_id": chat_id, "action": "typing"})
                except Exception:
                    pass

                # History
                if chat_id not in history:
                    history[chat_id] = []
                history[chat_id].append({"role": "user", "content": text})

                # Get response
                response = api_chat(text, history[chat_id])
                history[chat_id].append({"role": "assistant", "content": response})

                if len(history[chat_id]) > 12:
                    history[chat_id] = history[chat_id][-12:]

                # SINGLE message only
                try:
                    tg_request("sendMessage", {"chat_id": chat_id, "text": response})
                except Exception as e:
                    log.error(f"Send failed: {e}")

                log.info(f"Sent to {chat_id} ({len(response)} chars)")

        except KeyboardInterrupt:
            break
        except Exception as e:
            log.error(f"Poll error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
