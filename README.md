# Phantom Node

Free Windows VPS via AppVeyor with Hermes pre-installed.

## Setup

1. **Configure Secrets** (optional but recommended):
   - Go to repo → Settings → Secrets and variables → Actions
   - Add `BOT_TOKEN` — your Telegram bot token
   - Add `XIAOMI_API_KEY` — your Mimo API key
   - If not set, falls back to hardcoded defaults

2. **Run Workflow**:
   - Go to Actions → Deploy → Run workflow
   - Optionally provide an `api_key` (overrides secrets)

3. **Connect**:
   - Read `CONNECTION.md` for SSH/RDP details
   - SSH: `ssh appveyor@<tunnel-url>`
   - Gateway auto-starts on login via Task Scheduler

## Files

| File | Purpose |
|------|---------|
| `~/.hermes/config.yaml` | Main config |
| `~/.hermes/.env` | API keys |
| `C:\start.bat` | Start gateway |
| `C:\cli.bat` | Interactive CLI |

## Dev Tools Included

- **Python**: flask, fastapi, uvicorn, pandas, numpy, pytest, black, ruff
- **Node.js**: typescript, ts-node, nodemon, pm2, yarn, pnpm
- **Docker**: CLI only (no daemon)
- **Hermes**: agent + gateway + all toolsets

## Secrets

| Secret | Description | Required |
|--------|-------------|----------|
| `BOT_TOKEN` | Telegram bot token | No (default built-in) |
| `XIAOMI_API_KEY` | Mimo API key | No (enter at dispatch) |
