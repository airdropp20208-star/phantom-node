#!/usr/bin/env python3
"""
Phantom Node v4 - Chat + Shell Execution
Can run commands on GitHub Actions runner
"""
import os
import json
import logging
import time
import subprocess
import urllib.request
import urllib.error

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
API_KEY = os.environ.get("API_KEY", "")
API_BASE = os.environ.get("API_BASE", "https://api.xiaomimimo.com/v1")
MODEL = os.environ.get("MODEL", "mimo-v2.5")
ALLOWED_CHATS = os.environ.get("ALLOWED_CHATS", "")
SHELL_PASSWORD = os.environ.get("SHELL_PASSWORD", "phantom123")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("phantom")

SYSTEM_PROMPT = (
    "You are PhantomBot. Rules:\n"
    "1. Reply in 1-2 sentences\n"
    "2. No markdown\n"
    "3. No lists\n"
    "4. Code: max 5 lines\n"
    "5. You are PhantomBot on Xiaomi MiMo\n"
    "6. If unclear: 'Làm rõ câu hỏi'"
)

last_response = {}
RATE_LIMIT = 3


def run_shell(cmd, timeout=30):
    """Execute shell command and return output"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout + result.stderr
        if not output:
            return "(no output)"
        # Truncate long output
        if len(output) > 1500:
            output = output[:1497] + "..."
        return output.strip()
    except subprocess.TimeoutExpired:
        return "⚠️ Command timed out"
    except Exception as e:
        return f"⚠️ Error: {str(e)[:200]}"


def api_chat(message, history=None):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history[-6:])
    messages.append({"role": "user", "content": message})

    payload = json.dumps({
        "model": MODEL,
        "messages": messages,
        "max_tokens": 300,
        "temperature": 0.2,
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
        if len(content) > 800:
            content = content[:797] + "..."
        return content.strip()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        log.error(f"API HTTP {e.code}: {body}")
        return f"⚠️ API error {e.code}"
    except Exception as e:
        log.error(f"API error: {e}")
        return "⚠️ API error"


def tg_request(method, data=None, timeout=10):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    req_data = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=req_data)
    if req_data:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def handle_command(chat_id, text):
    """Handle special commands"""
    lower = text.lower().strip()

    # Shell unlock
    if lower.startswith("!auth "):
        password = text[6:].strip()
        if password == SHELL_PASSWORD:
            return "✅ Shell access granted. Dùng !cmd <lệnh> để chạy"
        return "❌ Sai password"

    # Shell execution
    if lower.startswith("!cmd "):
        cmd = text[5:].strip()
        if not cmd:
            return "❌ Thiếu lệnh"
        log.info(f"Executing: {cmd}")
        output = run_shell(cmd)
        return f"```\n{output}\n```"

    # Quick commands
    if lower == "!scan":
        output = run_shell("uname -a && whoami && pwd && df -h / && free -h")
        return f"```\n{output}\n```"

    if lower == "!net":
        output = run_shell("ip addr show 2>/dev/null || ifconfig")
        return f"```\n{output}\n```"

    if lower == "!ps":
        output = run_shell("ps aux --sort=-%mem | head -15")
        return f"```\n{output}\n```"

    if lower == "!disk":
        output = run_shell("df -h && echo '---' && du -sh /* 2>/dev/null | sort -rh | head -10")
        return f"```\n{output}\n```"

    if lower in ("/clear", "/reset"):
        return "__CLEAR__"

    if lower == "/start":
        return "🤖 PhantomBot v4\n\nLệnh:\n!scan - thông tin máy\n!net - mạng\n!ps - processes\n!disk - ổ đĩa\n!cmd <lệnh> - chạy lệnh\n!auth <pw> - mở shell"

    if lower == "/status":
        return f"🤖 Model: {MODEL}\n📡 API: {API_BASE}\n🔐 Shell: locked"

    return None  # Not a command


def main():
    if not BOT_TOKEN or not API_KEY:
        log.error("Missing BOT_TOKEN or API_KEY!")
        return

    allowed = set(int(cid.strip()) for cid in ALLOWED_CHATS.split(",") if cid.strip())
    log.info(f"Bot v4 started! Model: {MODEL}")
    log.info(f"Allowed chats: {allowed or 'ALL'}")

    # Skip old messages
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
            for update in result.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message")
                if not msg:
                    continue

                chat_id = msg["chat"]["id"]
                text = msg.get("text", "")
                if not text:
                    continue

                if msg.get("from", {}).get("is_bot"):
                    continue

                if allowed and chat_id not in allowed:
                    continue

                # Rate limit
                now = time.time()
                if chat_id in last_response and now - last_response[chat_id] < RATE_LIMIT:
                    continue
                last_response[chat_id] = now

                log.info(f"[{chat_id}] {text[:80]}")

                # Handle commands first
                cmd_result = handle_command(chat_id, text)
                if cmd_result == "__CLEAR__":
                    history.pop(chat_id, None)
                    tg_request("sendMessage", {"chat_id": chat_id, "text": "✅ Reset"})
                    continue

                if cmd_result:
                    try:
                        tg_request("sendMessage", {"chat_id": chat_id, "text": cmd_result, "parse_mode": "Markdown"})
                    except Exception:
                        tg_request("sendMessage", {"chat_id": chat_id, "text": cmd_result})
                    continue

                # Typing
                try:
                    tg_request("sendChatAction", {"chat_id": chat_id, "action": "typing"})
                except Exception:
                    pass

                # Chat with AI
                if chat_id not in history:
                    history[chat_id] = []
                history[chat_id].append({"role": "user", "content": text})

                response = api_chat(text, history[chat_id])
                history[chat_id].append({"role": "assistant", "content": response})

                if len(history[chat_id]) > 12:
                    history[chat_id] = history[chat_id][-12:]

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
