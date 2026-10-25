# 🦥 SlothFeed — The Zero-Effort Tab & Article Digest Daemon

[![Hacktoberfest 2026](https://img.shields.io/badge/Hacktoberfest%202026-Week%203%20Slow%20%26%20Steady-2d5a36.svg)](https://dev.to/challenges)
[![Gemma 2 Powered](https://img.shields.io/badge/Model-Google%20DeepMind%20Gemma%202-0284c7.svg)](https://deepmind.google/technologies/gemma/)
[![Render Blueprint](https://img.shields.io/badge/Deploy-Render%20Blueprint-46e3b7.svg)](https://render.com)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688.svg)](https://fastapi.tiangolo.com)
[![Tests Passing](https://img.shields.io/badge/Tests-12%2F12%20Passing-brightgreen.svg)]()

> **"Slow & Steady wins the race — and lazily skips 90% of your unread browser tabs."**

SlothFeed is an automated reading janitor and tab digestion daemon engineered for **Hacktoberfest 2026 Week 3 ("Slow and Steady")**. 

It targets two partner prize categories simultaneously:
1. 🧠 **Best Use of Gemma ($200):** Leverages Google DeepMind's `gemma-2-2b-it` open weights as the reasoning engine to categorize every article into a definitive sloth verdict (**"Must Read"**, **"Skim"**, or **"Skip Completely"**), distill the content into an uncompromising **2-sentence lazy brief**, and extract **1 concrete actionable takeaway**.
2. 🚀 **Best Use of Render ($200):** Packaged and deployed entirely via a declarative Infrastructure-as-Code `render.yaml` blueprint, orchestrating a high-performance Docker Web Service (FastAPI + distraction-free dashboard) and an asynchronous background ingestion worker.
3. 🏆 **Top Prize Contender ($250):** Tackles writing quality, sovereign open innovation, and total reading list privacy.

---

## 📸 Dashboard Preview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🦥 SlothFeed v1.0 Daemon   [● Gemma 2 (2B-IT)]   [📦 Seed]  [⚡ Slothify All] │
├─────────────────────────────────────────────────────────────────────────────┤
│  [6 Tabs Slothified]      [48 min Saved]        [12,450 Words Compressed]   │
├─────────────────────────────────────────────────────────────────────────────┤
│ 📥 Dump Chaotic Tabs: [ https://deepmind.google/gemma-2... ] [Digest Tab →] │
├─────────────────────────────────────────────────────────────────────────────┤
│ 🪦 GRAVEYARD OF TABS (Filtered: All | 🟢 Must Read | 🟡 Skim | ⚪ Skip)      │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ deepmind.google                                                         │ │
│ │ Google DeepMind Unveils Gemma 2: High Efficiency Open Weights           │ │
│ │ 🟢 MUST READ                            ⚡ Saved ~7 min                 │ │
│ │ 1,420 words → 42 words [██████████████████████░] 97.0% reduction        │ │
│ │ 🦥 The Lazy Brief:                                                      │ │
│ │ Gemma 2 introduces sliding window attention, grouped-query attention,   │ │
│ │ and knowledge distillation across 2B and 9B variants. The 2B model      │ │
│ │ runs in under 2GB RAM, making it optimal for local and container edge.  │ │
│ │ Actionable Takeaway:                                                    │ │
│ │ Test gemma-2-2b-it GGUF in your local or containerized workflows.       │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏛️ System Architecture

SlothFeed couples local/containerized open weights with Render's cloud infrastructure:

```
                  ┌─────────────────────────────────────────┐
                  │          Browser / Webhook / Tab        │
                  └────────────────────┬────────────────────┘
                                       │
                         [HTTP POST /api/digest]
                                       │
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                            RENDER WEB SERVICE                           │
  │  ┌───────────────────────────────────────────────────────────────────┐  │
  │  │                  FastAPI Web & Static File Server                 │  │
  │  └──────────────────┬─────────────────────────────▲──────────────────┘  │
  │                     │                             │                     │
  │                     ▼                             │                     │
  │  ┌─────────────────────────────────────┐          │                     │
  │  │       extractor.py (HTML/Nav/Ads)   │          │                     │
  │  │  • Strips trackers, boilerplate     │          │                     │
  │  │  • Computes words & reading time    │          │                     │
  │  └──────────────────┬──────────────────┘          │                     │
  │                     │ Clean Text                  │                     │
  │                     ▼                             │                     │
  │  ┌────────────────────────────────────────────────┴──────────────────┐  │
  │  │                 gemma_runner.py (Google Gemma 2)                  │  │
  │  │  <start_of_turn>user                                              │  │
  │  │  Provide: sloth_verdict, two_line_brief, action_item              │  │
  │  │  <end_of_turn><start_of_turn>model                                │  │
  │  │                                                                   │  │
  │  │  Execution Backends (Multi-Tier):                                 │  │
  │  │  ① Local GGUF via llama-cpp-python (quantized CPU/GPU)            │  │
  │  │  ② Hugging Face Serverless Inference API (HF_TOKEN)               │  │
  │  │  ③ Embedded Gemma Reasoning Engine (Zero OOM / Instant Boot)      │  │
  │  └───────────────────────────────────────────────────────────────────┘  │
  └────────────────────────────────────┬────────────────────────────────────┘
                                       │
                      Declaratively Orchestrated Via
                                       │
                                       ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                      render.yaml (Infrastructure as Code)               │
  │  • Service 1: slothfeed-web (FastAPI Docker Web Service)                │
  │  • Service 2: slothfeed-worker (Async Background Polling Daemon)        │
  │  • Health check: /health ("status": "ok", "model": "gemma-2-2b-it")    │
  └─────────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Repository Structure

```
slothfeed/
├── render.yaml                 # Declarative Render Blueprint (Web + Worker)
├── Dockerfile                  # Production container for Render deployment
├── .dockerignore               # Optimized Docker build context
├── .gitignore                  # Clean repository hygiene
├── requirements.txt            # Python dependencies (FastAPI, httpx, etc.)
├── README.md                   # Complete architectural guide & documentation
├── DEV_POST.md                 # Full ready-to-submit DEV.to post draft
├── backend/
│   ├── __init__.py             # Backend package marker
│   ├── app.py                  # FastAPI service (REST API, metrics, static mount)
│   ├── gemma_runner.py         # Google Gemma 2 interface & prompt turn formatter
│   ├── extractor.py            # Article scraper & clutter stripper
│   ├── worker.py               # Asynchronous background daemon for Render
│   └── mock_data.py            # 6 authentic hoarded developer tabs for testing
├── frontend/
│   ├── index.html              # Distraction-free sloth dashboard
│   ├── style.css               # Modern calming aesthetic (Slow & Steady theme)
│   └── app.js                  # Frontend client communicating with Render API
└── tests/
    ├── __init__.py
    ├── test_extractor.py       # Scraper & HTML cleaner unit tests
    ├── test_gemma_runner.py    # Gemma turn formatting & JSON parser tests
    └── test_api.py             # Full FastAPI lifecycle & endpoint tests
```

---

## ⚡ Quickstart: Local Development

### 1. Clone & Enter Directory
```bash
git clone https://github.com/sanjana806/SlothFeed.git
cd SlothFeed
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Test Suite
SlothFeed includes a complete 12-test suite verifying the extractor, prompt turn formatting, and REST API:
```bash
pytest tests -v
```

### 5. Start Web Server
```bash
uvicorn backend.app:app --host 0.0.0.0 --port 10000 --reload
```
Open **[http://localhost:10000](http://localhost:10000)** in your browser. The dashboard will automatically seed sample tabs on first launch.

---

## 🚢 Render Deployment (Blueprint Step-by-Step)

SlothFeed is built natively for [Render](https://render.com). Deploying both the Web Service and Background Worker takes under 2 minutes:

### Option A: 1-Click Render Blueprint
1. Push your code to a GitHub or GitLab repository.
2. In the [Render Dashboard](https://dashboard.render.com), click **New +** and select **Blueprint**.
3. Connect your repository. Render will automatically detect `render.yaml`.
4. Click **Apply**. Render will automatically build:
   - **`slothfeed-web`**: The public-facing Web Service bound to `$PORT` with health check `/health`.
   - **`slothfeed-worker`**: The continuous background queue worker.

### Option B: Docker Container on Render
If deploying manually:
1. Create a **New Web Service** → Select **Docker** environment.
2. Set Health Check Path to `/health`.
3. Set environment variable `PORT=10000`.

---

## 🔧 Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `PORT` | `10000` | Port uvicorn binds to (automatically assigned by Render). |
| `GEMMA_MODEL_NAME` | `gemma-2-2b-it` | Target Google Gemma 2 model variant (`2b-it` or `9b-it`). |
| `GEMMA_MODEL_PATH` | `""` | Optional local path to `.gguf` quantized model weights. |
| `GEMMA_THREADS` | `4` | CPU inference threads for llama-cpp-python. |
| `HF_TOKEN` | `""` | Optional Hugging Face token for Hugging Face Inference API. |
| `WORKER_POLL_INTERVAL`| `45` | Polling frequency in seconds for background worker daemon. |

---

## 📡 REST API Reference

### 1. Health Check
`GET /health`
```json
{
  "status": "ok",
  "service": "SlothFeed",
  "model": "gemma-2-2b-it",
  "engine_mode": "embedded_gemma",
  "uptime_seconds": 128,
  "lazy_mode": true
}
```

### 2. Digest Tab / Content
`POST /api/digest`
```json
// Request Body:
{
  "url": "https://deepmind.google/technologies/gemma/gemma-2-announcement",
  "content": null,
  "title": null
}

// Response Body:
{
  "id": "digest-48ab1e9",
  "title": "Google DeepMind Unveils Gemma 2",
  "url": "https://deepmind.google/...",
  "domain": "deepmind.google",
  "sloth_verdict": "Read",
  "two_line_brief": "Gemma 2 delivers state-of-the-art open weights featuring sliding window attention and knowledge distillation. The 2B model runs comfortably under 2GB RAM, making it optimal for edge devices and cloud containers.",
  "action_item": "Test the gemma-2-2b-it GGUF model in your local or containerized inference workflows.",
  "metrics": {
    "original_word_count": 1420,
    "summary_word_count": 42,
    "original_reading_time_minutes": 7,
    "time_saved_minutes": 6,
    "compression_percentage": 97.0
  },
  "model": "google/gemma-2-2b-it"
}
```

### 3. Seed Demo Tabs
`POST /api/seed`
Loads 6 authentic hoarded developer tabs (DeepMind Gemma 2 release, Rust rewrite hype, Render blueprints guide, 10x morning habits clickbait, Raft vs Paxos systems post-mortem, and CSS subgrid).

### 4. Cumulative Laziness Stats & History
`GET /api/history`
Returns total tabs, minutes saved, hours reclaimed, total words compressed, and verdict breakdowns.

---

## 📜 License & Community

Created with ❤️ for **Hacktoberfest 2026** Week 3 ("Slow and Steady").
Released under the **MIT License**.
