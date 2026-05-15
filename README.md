<p align="center">
  <img src="https://img.shields.io/badge/PHANTOM%20NODE-v4.0-purple?style=for-the-badge&labelColor=black" />
  <img src="https://img.shields.io/badge/GOD%20MODE-ACTIVE-brightgreen?style=for-the-badge&labelColor=black" />
  <img src="https://img.shields.io/badge/STATUS-IMMORTAL-yellow?style=for-the-badge&labelColor=black" />
</p>

<h1 align="center"> phantom-node </h1>

<p align="center">
  <b>⚡ DeepSeek V4 Gateway + MITM Proxy + Coding Agent + Self-Healing ⚡</b><br>
  <sub>Your free Windows VPS for 60 minutes — pre-installed with everything</sub>
</p>

---

```
    ╔══════════════════════════════════════════════════════════════╗
    ║              PHANTOM NODE - GOD MODE v4.0                  ║
    ║                                                              ║
    ║   ┌──────────┐    ┌──────────┐    ┌──────────┐            ║
    ║   │  DeepSeek │───▶│  ds2api   │───▶│ 9Router  │──▶ IDE    ║
    ║   │    V4     │    │  :5001   │    │  :9090   │            ║
    ║   └──────────┘    └──────────┘    └──────────┘            ║
    ║         │              │              │                     ║
    ║         ▼              ▼              ▼                     ║
    ║   ┌────────────────────────────────────────────────┐      ║
    ║   │   DeepSeek-TUI  •  Self-Healing  •  Logs       │      ║
    ║   └────────────────────────────────────────────────┘      ║
    ╚══════════════════════════════════════════════════════════════╝
```

## 🔥 What is this?

**Phantom Node** turns AppVeyor's free Windows VM into a **fully-configured DeepSeek V4 development environment** with:

- **ds2api** — OpenAI/Claude/Gemini compatible API gateway
- **9router** — MITM proxy for transparent model aliasing  
- **DeepSeek-TUI** — Terminal coding agent (`deepseek` command)
- **Self-healing** — Auto-restarts crashed services every 60 seconds
- **Zero cost** — Runs on AppVeyor's free tier
- **Zero trace** — Self-destructs after 60 minutes

## ⚡ What You Get

| Service | Port | Purpose |
|---------|------|---------|
| ds2api | `:5001` | OpenAI-compatible API endpoint |
| 9router | `:9090` | MITM proxy (GPT-4o → DeepSeek) |
| DeepSeek-TUI | CLI | `deepseek` command in terminal |

## 🤖 Model Aliases

When any IDE/app requests these models, they get redirected to DeepSeek V4:

| Requested Model | → Mapped To |
|----------------|-------------|
| `gpt-4o` | `deepseek-v4-pro` |
| `gpt-4o-mini` | `deepseek-v4-flash` |
| `gpt-5` | `deepseek-v4-pro` |
| `o3` | `deepseek-v4-pro` |
| `claude-sonnet-4-20250514` | `deepseek-v4-pro` |
| `claude-3-5-haiku` | `deepseek-v4-flash` |
| `gemini-2.5-pro` | `deepseek-v4-pro` |
| `gemini-2.5-flash` | `deepseek-v4-flash` |

## 🚀 Quick Start

### 1. Fork this repo

### 2. Edit credentials in `appveyor.yml`

```yaml
environment:
  DS_EMAIL: "your-email@gmail.com"
  DS_PASSWORD: "your-password"
  API_KEY: "your-api-key"
```

### 3. Connect to AppVeyor

1. Go to [appveyor.com](https://appveyor.com)
2. Sign in with GitHub
3. Enable the phantom-node repo
4. Trigger a build

### 4. RDP into the machine

AppVeyor provides RDP credentials in the build log. Connect and use!

## 🛠️ Installation Steps (What Runs)

```
[1/7] Killing Windows services...     → 10 services disabled
[2/7] Installing Node 18 + Chrome...  → Runtime environment
[3/7] Installing DeepSeek-TUI...      → Coding agent (npm/cargo)
[4/7] Setting up ds2api...            → API gateway on :5001
[5/7] Setting up 9router...           → MITM proxy on :9090
[6/7] Configuring DeepSeek-TUI...     → Point to local ds2api
[7/7] Verifying services...           → Health check
```

## 📊 Features

| Feature | Status |
|---------|--------|
| DeepSeek V4 Flash/Pro | ✅ |
| OpenAI API compat (`/v1/*`) | ✅ |
| Claude API compat (`/anthropic/*`) | ✅ |
| Gemini API compat (`/v1beta/*`) | ✅ |
| MITM Proxy (9router) | ✅ |
| ds2api Gateway | ✅ |
| DeepSeek-TUI (coding agent) | ✅ |
| Self-healing processes | ✅ |
| Process priority boost | ✅ |
| RAM cleansing | ✅ |
| Service debloat (10 services) | ✅ |
| File logging | ✅ |
| Clean shutdown | ✅ |

## 🎯 DeepSeek-TUI

Terminal coding agent included. After build:

```bash
# Just type 'deepseek' in terminal
deepseek

# Features:
# - Auto mode (chooses model + thinking level)
# - Streaming reasoning blocks
# - File ops, shell, git, web search
# - 1M-token context window
# - MCP protocol support
# - Skills system
```

## 🛡️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AppVeyor Windows VM                      │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   DeepSeek    │    │    ds2api    │    │   9router    │  │
│  │   V4 API      │───▶│   :5001      │───▶│    :9090     │──▶ IDE
│  │   (external)  │    │   (local)    │    │   (MITM)     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                              │                               │
│                              ▼                               │
│                     ┌──────────────┐                        │
│                     │ DeepSeek-TUI │                        │
│                     │  (coding)    │                        │
│                     └──────────────┘                        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Self-Healing Loop (60 min) • Health Checks • Logs   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 📈 Performance

| Metric | Value |
|--------|-------|
| Cold start | ~3 min |
| ds2api response | <100ms |
| MITM latency | <50ms |
| Max concurrent | 2/account |
| Token refresh | Every 6 hours |
| Session duration | 60 minutes |

## ⚠️ Disclaimer

This project is for **educational purposes only**.

- Don't use for commercial purposes
- Don't abuse AppVeyor's free tier
- Don't violate any ToS
- You are responsible for your actions

## 📜 License

MIT License — Do whatever you want

---

<p align="center">
  <img src="https://img.shields.io/badge/MADE%20WITH-%E2%9D%A4%EF%B8%8F-red?style=flat-square" />
  <img src="https://img.shields.io/badge/BY-AIRDROPP20208--STAR-blue?style=flat-square" />
  <img src="https://img.shields.io/badge/SERVING-DEEPSEEK%20V4-purple?style=flat-square" />
</p>
