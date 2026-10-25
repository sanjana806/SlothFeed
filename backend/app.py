"""
SlothFeed FastAPI Web Service.
Automated reading janitor and article digestion daemon powered by Google Gemma 2.
"""

import os
import time
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.extractor import fetch_and_clean_url, clean_raw_text, calculate_reading_time
from backend.gemma_runner import GemmaRunner
from backend.mock_data import get_mock_articles

# Initialize FastAPI App
app = FastAPI(
    title="SlothFeed API",
    description="Automated reading janitor & article digestion daemon powered by Google Gemma 2 and Render.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Application State
START_TIME = time.time()
gemma_engine = GemmaRunner()
DIGEST_HISTORY: List[Dict[str, Any]] = []


# Request / Response Schemas
class DigestRequest(BaseModel):
    url: Optional[str] = Field(None, description="Article URL to extract and digest")
    content: Optional[str] = Field(None, description="Pasted article text or markdown")
    title: Optional[str] = Field(None, description="Optional custom title")


class BatchDigestRequest(BaseModel):
    urls: List[str] = Field(default_factory=list, description="List of URLs to digest in batch")


class SeedRequest(BaseModel):
    auto_slothify: bool = Field(True, description="Whether to run Gemma digestion on the seed items immediately")


# Helper Functions
def compute_metrics(original_word_count: int, summary_text: str):
    """Calculates reading times, compression ratio, and time saved."""
    summary_words = len(summary_text.split())
    orig_time = calculate_reading_time(original_word_count)
    summary_time = max(1, calculate_reading_time(summary_words)) if summary_words > 0 else 0
    time_saved = max(0, orig_time - (1 if orig_time > 1 else 0))
    compression_percent = round((1.0 - (summary_words / max(1, original_word_count))) * 100, 1)

    return {
        "original_word_count": original_word_count,
        "summary_word_count": summary_words,
        "original_reading_time_minutes": orig_time,
        "time_saved_minutes": time_saved,
        "compression_percentage": max(0.0, min(99.9, compression_percent))
    }


# API Endpoints
@app.get("/health")
async def health_check():
    """
    Render Health Check Endpoint.
    Verifies service vitality and reports active Gemma model.
    """
    return {
        "status": "ok",
        "service": "SlothFeed",
        "model": "gemma-2-2b-it",
        "engine_mode": gemma_engine.mode,
        "uptime_seconds": int(time.time() - START_TIME),
        "lazy_mode": True
    }


@app.post("/api/digest")
async def create_digest(req: DigestRequest):
    """
    Extracts article content from URL or raw text,
    invokes Gemma 2 reasoning, and records the lazy digest.
    """
    if not req.url and not req.content:
        raise HTTPException(status_code=400, detail="Provide either an article URL or raw text content.")

    # 1. Extraction Phase
    if req.url:
        extracted = await fetch_and_clean_url(req.url)
        if not extracted["success"] and not req.content:
            raise HTTPException(status_code=422, detail=f"Failed to fetch content from URL: {extracted.get('error')}")
    else:
        extracted = clean_raw_text(req.content or "", custom_title=req.title)

    title = req.title or extracted.get("title", "Untitled Tab")
    article_text = extracted.get("text", "") or req.content or ""

    if len(article_text.strip()) < 20:
        raise HTTPException(status_code=422, detail="Extracted article text is too short for meaningful distillation.")

    # 2. Gemma 2 Reasoning Phase
    gemma_result = await gemma_engine.generate_digest(article_text, title=title)

    # 3. Metrics Calculation
    metrics = compute_metrics(extracted["word_count"], gemma_result["two_line_brief"])

    # 4. Record Packaging
    record = {
        "id": f"digest-{uuid.uuid4().hex[:10]}",
        "title": title,
        "url": req.url or "direct://pasted",
        "domain": extracted.get("domain", "direct-input"),
        "sloth_verdict": gemma_result["sloth_verdict"],
        "two_line_brief": gemma_result["two_line_brief"],
        "action_item": gemma_result["action_item"],
        "metrics": metrics,
        "raw_snippet": extracted.get("snippet", ""),
        "model": gemma_result["model"],
        "engine_mode": gemma_result["engine_mode"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    # Prepend to history (newest first)
    DIGEST_HISTORY.insert(0, record)
    return record


@app.post("/api/batch-digest")
async def batch_digest(req: BatchDigestRequest):
    """Digests multiple URLs concurrently."""
    results = []
    for url in req.urls:
        if not url.strip():
            continue
        try:
            item = await create_digest(DigestRequest(url=url.strip()))
            results.append(item)
        except Exception as e:
            results.append({"url": url, "error": str(e), "success": False})
    return {"processed": len(results), "items": results}


@app.post("/api/seed")
async def seed_articles(req: SeedRequest = SeedRequest()):
    """
    Seeds pre-curated authentic developer tabs.
    If auto_slothify is True, automatically digests them with Gemma 2.
    """
    mock_articles = get_mock_articles()
    seeded_records = []

    for item in mock_articles:
        raw_text = item["raw_content"].strip()
        word_count = len(raw_text.split())

        if req.auto_slothify:
            gemma_result = await gemma_engine.generate_digest(raw_text, title=item["title"])
            metrics = compute_metrics(word_count, gemma_result["two_line_brief"])
            record = {
                "id": f"seed-{item['id']}",
                "title": item["title"],
                "url": item["url"],
                "domain": item["url"].split("/")[2] if "/" in item["url"] else "mock-source",
                "sloth_verdict": gemma_result["sloth_verdict"],
                "two_line_brief": gemma_result["two_line_brief"],
                "action_item": gemma_result["action_item"],
                "metrics": metrics,
                "raw_snippet": raw_text[:350] + "...",
                "model": gemma_result["model"],
                "engine_mode": gemma_result["engine_mode"],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        else:
            # Pending unread state
            metrics = compute_metrics(word_count, "")
            record = {
                "id": f"seed-{item['id']}",
                "title": item["title"],
                "url": item["url"],
                "domain": item["url"].split("/")[2] if "/" in item["url"] else "mock-source",
                "sloth_verdict": "Pending",
                "two_line_brief": "Waiting for Slothify action...",
                "action_item": "Click 'Slothify All' to distill.",
                "metrics": metrics,
                "raw_snippet": raw_text[:350] + "...",
                "model": "google/gemma-2-2b-it",
                "engine_mode": gemma_engine.mode,
                "created_at": datetime.now(timezone.utc).isoformat()
            }

        # Check if already present to prevent duplicate accumulation on multiple clicks
        existing_idx = next((i for i, d in enumerate(DIGEST_HISTORY) if d["id"] == record["id"]), None)
        if existing_idx is not None:
            DIGEST_HISTORY[existing_idx] = record
        else:
            DIGEST_HISTORY.append(record)
        seeded_records.append(record)

    return {"seeded_count": len(seeded_records), "items": seeded_records}


@app.get("/api/history")
async def get_history(filter_verdict: Optional[str] = Query(None)):
    """
    Retrieves stored digest records and cumulative laziness statistics.
    """
    items = DIGEST_HISTORY
    if filter_verdict and filter_verdict.lower() != "all":
        items = [i for i in items if i.get("sloth_verdict", "").lower() == filter_verdict.lower()]

    # Compute aggregate stats
    total_tabs = len(DIGEST_HISTORY)
    total_minutes_saved = sum(i.get("metrics", {}).get("time_saved_minutes", 0) for i in DIGEST_HISTORY)
    total_words_original = sum(i.get("metrics", {}).get("original_word_count", 0) for i in DIGEST_HISTORY)
    total_words_distilled = sum(i.get("metrics", {}).get("summary_word_count", 0) for i in DIGEST_HISTORY)
    total_words_saved = max(0, total_words_original - total_words_distilled)

    breakdown = {
        "Read": sum(1 for i in DIGEST_HISTORY if i.get("sloth_verdict") == "Read"),
        "Skim": sum(1 for i in DIGEST_HISTORY if i.get("sloth_verdict") == "Skim"),
        "Skip": sum(1 for i in DIGEST_HISTORY if i.get("sloth_verdict") == "Skip"),
        "Pending": sum(1 for i in DIGEST_HISTORY if i.get("sloth_verdict") == "Pending"),
    }

    return {
        "stats": {
            "total_tabs": total_tabs,
            "total_minutes_saved": total_minutes_saved,
            "total_hours_saved": round(total_minutes_saved / 60, 1),
            "total_words_saved": total_words_saved,
            "breakdown": breakdown
        },
        "items": items
    }


@app.delete("/api/history/{item_id}")
async def delete_history_item(item_id: str):
    """Removes a single item from history."""
    global DIGEST_HISTORY
    initial_len = len(DIGEST_HISTORY)
    DIGEST_HISTORY = [i for i in DIGEST_HISTORY if i.get("id") != item_id]
    if len(DIGEST_HISTORY) == initial_len:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "deleted", "id": item_id}


@app.delete("/api/history")
async def clear_history():
    """Clears all digested tab history."""
    global DIGEST_HISTORY
    count = len(DIGEST_HISTORY)
    DIGEST_HISTORY = []
    return {"status": "cleared", "count": count}


# Mount Static Frontend
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
