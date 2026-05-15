<p align="center">
  <img src="https://img.shields.io/badge/PHANTOM%20NODE-v3.0-purple?style=for-the-badge&labelColor=black" />
  <img src="https://img.shields.io/badge/GOD%20MODE-ACTIVE-brightgreen?style=for-the-badge&labelColor=black" />
  <img src="https://img.shields.io/badge/STATUS-IMMORTAL-yellow?style=for-the-badge&labelColor=black" />
</p>

<h1 align="center"> phantom-node </h1>

<p align="center">
  <b>⚡ DeepSeek V4 Gateway + MITM Proxy + Self-Healing ⚡</b><br>
  <sub>Transform any AI IDE into a DeepSeek-powered weapon</sub>
</p>

---

```
    ╔══════════════════════════════════════════════════════╗
    ║          PHANTOM NODE - GOD MODE v3.0               ║
    ║                                                      ║
    ║   ┌─────────┐    ┌─────────┐    ┌─────────┐        ║
    ║   │  DeepSeek │───▶│  9Router │───▶│   IDE   │        ║
    ║   │   V4 API  │    │  (MITM)  │    │ (Any)   │        ║
    ║   └─────────┘    └─────────┘    └─────────┘        ║
    ║         │              │              │              ║
    ║         ▼              ▼              ▼              ║
    ║   ┌──────────────────────────────────────────┐     ║
    ║   │  Self-Healing Loop • Health Checks • Logs │     ║
    ║   └──────────────────────────────────────────┘     ║
    ╚══════════════════════════════════════════════════════╝
```

## 🔥 What is this?

**Phantom Node** is a CI/CD exploit that turns AppVeyor's free Windows VM into a persistent **DeepSeek V4 API gateway** with MITM proxy capabilities.

- **Zero cost** — runs on AppVeyor's free tier
- **Zero trace** — self-destructs after 60 minutes
- **Zero downtime** — self-healing process monitoring
- **Maximum power** — DeepSeek V4 Flash/Pro on demand

## ⚡ Features

| Feature | Status |
|---------|--------|
| DeepSeek V4 Flash/Pro/NoThinking | ✅ Active |
| OpenAI API compatibility | ✅ `/v1/*` |
| Claude API compatibility | ✅ `/anthropic/*` |
| Gemini API compatibility | ✅ `/v1beta/*` |
| MITM Proxy (9router) | ✅ Port 9090 |
| ds2api Gateway | ✅ Port 5001 |
| Self-healing processes | ✅ Auto-restart |
| Health monitoring | ✅ 60-min loop |
| Process priority boost | ✅ High priority |
| RAM cleansing | ✅ `EmptyWorkingSet` |
| Service debloat | ✅ 10 services killed |
| File logging | ✅ Desktop log |
| Clean shutdown | ✅ No traces |

## 🚀 Quick Start

### 1. Fork this repo

### 2. Set environment variables

In `appveyor.yml`, replace the placeholders:

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

## 🎯 Supported Models

| Model | Alias |
|-------|-------|
| `deepseek-v4-pro` | gpt-4o, gpt-5, claude-sonnet, o3, gemini-2.5-pro |
| `deepseek-v4-flash` | gpt-4o-mini, claude-3.5-haiku, gemini-2.5-flash |
| `deepseek-v4-flash-nothinking` | gemini-2.5-flash-lite |

## 🛡️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     AppVeyor VM                         │
│                                                         │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐         │
│  │  ds2api   │───▶│ 9router  │───▶│   IDE    │         │
│  │  :5001    │    │  :9090   │    │ (any)    │         │
│  └────┬─────┘    └──────────┘    └──────────┘         │
│       │                                                 │
│       ▼                                                 │
│  ┌──────────┐                                          │
│  │ DeepSeek │                                          │
│  │    V4    │                                          │
│  └──────────┘                                          │
└─────────────────────────────────────────────────────────┘
```

## 🔧 How it works

1. **Debloat** — Kills Windows Defender + 9 background services
2. **Install** — Node.js 18 + Chrome (for browser-based auth)
3. **ds2api** — Downloads & configures DeepSeek API gateway
4. **9router** — Sets up MITM proxy with model aliasing
5. **Monitor** — 60-minute self-healing loop with health checks
6. **Cleanup** — Destroys all traces on exit

## 📊 Performance

| Metric | Value |
|--------|-------|
| Cold start | ~3 min |
| ds2api response | <100ms |
| MITM latency | <50ms |
| Max concurrent | 2/account |
| Token refresh | Every 6 hours |

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
  <b>"The only way to do great work is to love what you do."</b><br>
  <sub>— Steve Jobs</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/MADE%20WITH-%E2%9D%A4%EF%B8%8F-red?style=flat-square" />
  <img src="https://img.shields.io/badge/BY-AIRDROPP20208--STAR-blue?style=flat-square" />
</p>
