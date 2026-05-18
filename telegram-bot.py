#!/usr/bin/env python3
"""
Phantom Node - Telegram Bot
Telegram → Claude Code → 9router → ds2api → DeepSeek
"""
import os
import subprocess
import json
import logging
from pathlib import Path

# Config
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ALLOWED_USERS = os.environ.get("ALLOWED_USERS", "").split(",")
WORKDIR = os.environ.get("WORKDIR", os.path.expanduser("~"))
ANTHROPIC_BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "http://localhost:20128/v1")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "sk-phantom")

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("phantom-bot")

def call_claude(message: str, timeout: int = 300) -> str:
    """Call Claude Code CLI with a message and return the response."""
    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = ANTHROPIC_BASE_URL
    env["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
    env["HOME"] = os.path.expanduser("~")
    env["PATH"] = "/usr/local/bin:/usr/bin:/bin:" + env.get("PATH", "")

    cmd = [
        "claude",
        "-p", message,
        "--output-format", "json",
        "--max-turns", "20",
        "--bare",
    ]

    try:
        logger.info(f"Running: {' '.join(cmd[:3])}...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=WORKDIR,
            env=env,
        )

        logger.info(f"Exit code: {result.returncode}")
        if result.stderr:
            logger.info(f"Stderr: {result.stderr[:500]}")

        if result.returncode != 0:
            error_msg = result.stderr[:500] if result.stderr else "No stderr"
            return f"Error (code {result.returncode}): {error_msg}"

        # Parse JSON response
        try:
            data = json.loads(result.stdout)
            return data.get("result", result.stdout[:2000])
        except json.JSONDecodeError:
            return result.stdout[:2000] if result.stdout else "No response"

    except subprocess.TimeoutExpired:
        return "Timeout - task took too long"
    except FileNotFoundError:
        return "Error: claude command not found. Is Claude Code installed?"
    except Exception as e:
        return f"Error: {str(e)[:200]}"


def main():
    """Simple Telegram bot using polling."""
    import urllib.request
    import urllib.parse
    import time

    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set!")
        return

    API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"
    offset = 0

    logger.info("Phantom Bot started!")
    logger.info(f"Workdir: {WORKDIR}")
    logger.info(f"ANTHROPIC_BASE_URL: {ANTHROPIC_BASE_URL}")

    while True:
        try:
            # Get updates
            url = f"{API_BASE}/getUpdates?offset={offset}&timeout=30"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = json.loads(resp.read())

            for update in data.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message", {})
                if not msg:
                    continue

                chat_id = msg["chat"]["id"]
                user_id = str(msg.get("from", {}).get("id", ""))
                text = msg.get("text", "")

                # Check allowed users
                if ALLOWED_USERS != [""] and user_id not in ALLOWED_USERS:
                    logger.info(f"Ignored message from unauthorized user {user_id}")
                    continue

                if not text:
                    continue

                logger.info(f"Message from {user_id}: {text[:100]}")

                # Send "typing" indicator
                try:
                    typing_url = f"{API_BASE}/sendChatAction"
                    typing_data = json.dumps({"chat_id": chat_id, "action": "typing"}).encode()
                    urllib.request.Request(typing_url, data=typing_data, headers={"Content-Type": "application/json"})
                    urllib.request.urlopen(urllib.request.Request(
                        typing_url,
                        data=typing_data,
                        headers={"Content-Type": "application/json"}
                    ), timeout=10)
                except:
                    pass

                # Call Claude Code
                response = call_claude(text)

                # Send response
                send_url = f"{API_BASE}/sendMessage"
                send_data = json.dumps({
                    "chat_id": chat_id,
                    "text": response[:4000],
                    "parse_mode": "Markdown",
                }).encode()

                try:
                    urllib.request.urlopen(urllib.request.Request(
                        send_url,
                        data=send_data,
                        headers={"Content-Type": "application/json"}
                    ), timeout=10)
                except:
                    # Retry without markdown
                    send_data = json.dumps({
                        "chat_id": chat_id,
                        "text": response[:4000],
                    }).encode()
                    urllib.request.urlopen(urllib.request.Request(
                        send_url,
                        data=send_data,
                        headers={"Content-Type": "application/json"}
                    ), timeout=10)

                logger.info(f"Response sent to {chat_id}")

        except KeyboardInterrupt:
            logger.info("Bot stopped!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
