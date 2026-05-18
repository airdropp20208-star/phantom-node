#!/usr/bin/env python3
"""
Phantom Node v6 - Chat + Shell + File Transfer
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
RATE_LIMIT = 2


def run_shell(cmd, timeout=30):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        output = result.stdout + result.stderr
        if not output:
            return "(no output)"
        if len(output) > 2000:
            output = output[:1997] + "..."
        return output.strip()
    except subprocess.TimeoutExpired:
        return "⚠️ Timeout"
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
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"},
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


def tg_upload(method, file_path, chat_id, caption=""):
    """Upload file to Telegram"""
    import mimetypes
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    
    filename = os.path.basename(file_path)
    mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    
    with open(file_path, "rb") as f:
        file_data = f.read()
    
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="chat_id"\r\n\r\n'
        f"{chat_id}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="caption"\r\n\r\n'
        f"{caption}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="document"; filename="{filename}"\r\n'
        f"Content-Type: {mime_type}\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    req = urllib.request.Request(url, data=body)
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def send_msg(chat_id, text):
    if len(text) <= 4096:
        try:
            tg_request("sendMessage", {"chat_id": chat_id, "text": text})
        except Exception as e:
            log.error(f"Send failed: {e}")
    else:
        for i in range(0, len(text), 4096):
            try:
                tg_request("sendMessage", {"chat_id": chat_id, "text": text[i:i+4096]})
            except Exception as e:
                log.error(f"Send chunk failed: {e}")


def handle_document(chat_id, document):
    """Handle file upload from user"""
    file_id = document.get("file_id")
    file_name = document.get("file_name", "unknown")
    file_size = document.get("file_size", 0)
    
    if file_size > 50 * 1024 * 1024:  # 50MB limit
        send_msg(chat_id, "⚠️ File quá lớn (max 50MB)")
        return
    
    # Get file path
    try:
        file_info = tg_request("getFile", {"file_id": file_id})
        file_path = file_info["result"]["file_path"]
        download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        
        # Download to /tmp
        local_path = f"/tmp/{file_name}"
        urllib.request.urlretrieve(download_url, local_path)
        
        send_msg(chat_id, f"✅ Đã nhận: {file_name} ({file_size} bytes)\nĐường dẫn: {local_path}")
        log.info(f"Received file: {file_name} -> {local_path}")
    except Exception as e:
        send_msg(chat_id, f"⚠️ Lỗi nhận file: {str(e)[:100]}")
        log.error(f"File download error: {e}")


def main():
    if not BOT_TOKEN or not API_KEY:
        log.error("Missing BOT_TOKEN or API_KEY!")
        return

    allowed = set(int(cid.strip()) for cid in ALLOWED_CHATS.split(",") if cid.strip())
    log.info(f"Bot v6 started! Model: {MODEL}")
    log.info(f"Allowed chats: {allowed or 'ALL'}")

    # Skip old messages
    try:
        result = tg_request("getUpdates", {"offset": -1, "timeout": 1}, timeout=5)
        offset = result["result"][-1]["update_id"] + 1 if result.get("result") else 0
        log.info(f"Skipped to offset {offset}")
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
                
                # Handle file uploads
                if msg.get("document"):
                    if allowed and chat_id not in allowed:
                        continue
                    handle_document(chat_id, msg["document"])
                    continue
                
                if not text or msg.get("from", {}).get("is_bot"):
                    continue

                if allowed and chat_id not in allowed:
                    continue

                # Rate limit
                now = time.time()
                if chat_id in last_response and now - last_response[chat_id] < RATE_LIMIT:
                    continue
                last_response[chat_id] = now

                log.info(f"[{chat_id}] {text[:80]}")

                # Typing
                try:
                    tg_request("sendChatAction", {"chat_id": chat_id, "action": "typing"})
                except Exception:
                    pass

                lower = text.lower().strip()

                # === COMMANDS ===
                if lower in ("/clear", "/reset"):
                    history.pop(chat_id, None)
                    send_msg(chat_id, "✅ Reset")
                    continue

                if lower == "/start":
                    send_msg(chat_id, "🤖 PhantomBot v6\n\nLệnh:\n!cmd <lệnh> - chạy lệnh\n!scan - thông tin hệ thống\n!net - mạng\n!ps - processes\n!disk - ổ đĩa\n!whoami - user info\n!env - environment\n!python <code> - chạy Python\n!sh <script> - chạy shell script\n!upload <đường dẫn> - gửi file\n\nGửi file để lưu vào /tmp/")
                    continue

                # Shell commands
                if lower.startswith("!cmd "):
                    cmd = text[5:].strip()
                    output = run_shell(cmd)
                    send_msg(chat_id, f"```\n{output}\n```")
                    continue

                if lower == "!scan":
                    output = run_shell("uname -a && whoami && pwd && echo '---DISK---' && df -h / && echo '---MEM---' && free -h && echo '---CPU---' && nproc && cat /proc/cpuinfo | grep 'model name' | head -1")
                    send_msg(chat_id, f"```\n{output}\n```")
                    continue

                if lower == "!net":
                    output = run_shell("ip addr show 2>/dev/null || ifconfig && echo '---ROUTES---' && ip route && echo '---DNS---' && cat /etc/resolv.conf 2>/dev/null")
                    send_msg(chat_id, f"```\n{output}\n```")
                    continue

                if lower == "!ps":
                    output = run_shell("ps aux --sort=-%mem | head -20")
                    send_msg(chat_id, f"```\n{output}\n```")
                    continue

                if lower == "!disk":
                    output = run_shell("df -h && echo '===LARGE FILES===' && find / -type f -size +10M 2>/dev/null | head -20")
                    send_msg(chat_id, f"```\n{output}\n```")
                    continue

                if lower == "!whoami":
                    output = run_shell("whoami && id && hostname && cat /etc/os-release 2>/dev/null | head -5")
                    send_msg(chat_id, f"```\n{output}\n```")
                    continue

                if lower == "!env":
                    output = run_shell("env | sort")
                    send_msg(chat_id, f"```\n{output}\n```")
                    continue

                if lower.startswith("!python "):
                    code = text[9:].strip()
                    output = run_shell(f"python3 -c '{code}'", timeout=15)
                    send_msg(chat_id, f"```\n{output}\n```")
                    continue

                if lower.startswith("!sh "):
                    script = text[4:].strip()
                    output = run_shell(script, timeout=30)
                    send_msg(chat_id, f"```\n{output}\n```")
                    continue

                # File upload command
                if lower.startswith("!upload "):
                    file_path = text[8:].strip()
                    if not file_path.startswith("/"):
                        file_path = f"/tmp/{file_path}"
                    
                    if not os.path.exists(file_path):
                        send_msg(chat_id, f"❌ File không tồn tại: {file_path}")
                        continue
                    
                    file_size = os.path.getsize(file_path)
                    if file_size > 50 * 1024 * 1024:
                        send_msg(chat_id, "⚠️ File quá lớn (max 50MB)")
                        continue
                    
                    try:
                        send_msg(chat_id, f"📤 Đang gửi: {file_path} ({file_size} bytes)...")
                        tg_upload("sendDocument", file_path, chat_id, f"📁 {os.path.basename(file_path)}")
                        send_msg(chat_id, "✅ Đã gửi!")
                    except Exception as e:
                        send_msg(chat_id, f"⚠️ Lỗi gửi file: {str(e)[:100]}")
                    continue

                # === AI CHAT ===
                if chat_id not in history:
                    history[chat_id] = []
                history[chat_id].append({"role": "user", "content": text})

                response = api_chat(text, history[chat_id])
                history[chat_id].append({"role": "assistant", "content": response})

                if len(history[chat_id]) > 12:
                    history[chat_id] = history[chat_id][-12:]

                send_msg(chat_id, response)
                log.info(f"Sent to {chat_id} ({len(response)} chars)")

        except KeyboardInterrupt:
            break
        except Exception as e:
            log.error(f"Poll error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
