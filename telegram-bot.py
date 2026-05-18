#!/usr/bin/env python3
"""
Phantom Node - Telegram Bot
Telegram → Open Interpreter → DeepSeek V4 (FREE via ds2api)
"""
import os
import subprocess
import json
import logging
import time

# Config
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ALLOWED_USERS = os.environ.get("ALLOWED_USERS", "").split(",")
WORKDIR = os.environ.get("WORKDIR", os.path.expanduser("~"))
OPENAI_API_BASE = os.environ.get("OPENAI_API_BASE", "http://localhost:20128/v1")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-phantom")

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("phantom-bot")

def call_interpreter(message: str, timeout: int = 300) -> str:
    """Call Open Interpreter with a message and return the response."""
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = OPENAI_API_KEY
    env["OPENAI_API_BASE"] = OPENAI_API_BASE
    env["HOME"] = os.path.expanduser("~")
    env["PATH"] = "/usr/local/bin:/usr/bin:/bin:" + env.get("PATH", "")

    cmd = [
        "interpreter",
        "--print",
        "--model", "deepseek-v4-flash",
        "--api_base", OPENAI_API_BASE,
        "--api_key", OPENAI_API_KEY,
        message,
    ]

    try:
        logger.info(f"Running interpreter...")
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
            # Fallback: try without --print
            return f"Error (code {result.returncode}): {error_msg}"

        return result.stdout[:4000] if result.stdout else "No response"

    except subprocess.TimeoutExpired:
        return "Timeout - task took too long"
    except FileNotFoundError:
        return "Error: interpreter command not found. Is Open Interpreter installed?"
    except Exception as e:
        return f"Error: {str(e)[:200]}"


def main():
    """Simple Telegram bot using polling."""
    import urllib.request

    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set!")
        return

    API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"
    offset = 0

    logger.info("Phantom Bot started!")
    logger.info(f"Workdir: {WORKDIR}")
    logger.info(f"OPENAI_API_BASE: {OPENAI_API_BASE}")

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
                    urllib.request.urlopen(urllib.request.Request(
                        typing_url,
                        data=typing_data,
                        headers={"Content-Type": "application/json"}
                    ), timeout=10)
                except:
                    pass

                # Call Open Interpreter
                response = call_interpreter(text)

                # Send response
                send_url = f"{API_BASE}/sendMessage"
                send_data = json.dumps({
                    "chat_id": chat_id,
                    "text": response[:4000],
                }).encode()

                try:
                    urllib.request.urlopen(urllib.request.Request(
                        send_url,
                        data=send_data,
                        headers={"Content-Type": "application/json"}
                    ), timeout=10)
                except Exception as e:
                    logger.error(f"Failed to send: {e}")

                logger.info(f"Response sent to {chat_id}")

        except KeyboardInterrupt:
            logger.info("Bot stopped!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
