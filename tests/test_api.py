"""Integration tests for SlothFeed FastAPI endpoints."""

import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app import app


def test_health_check_endpoint():
    async def _test():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/health")
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "ok"
            assert data["service"] == "SlothFeed"
            assert data["model"] == "gemma-2-2b-it"

    asyncio.run(_test())


def test_seed_and_history_lifecycle():
    async def _test():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Clear existing history
            del_res = await client.delete("/api/history")
            assert del_res.status_code == 200

            # 2. Seed pre-curated articles
            seed_res = await client.post("/api/seed", json={"auto_slothify": True})
            assert seed_res.status_code == 200
            seed_data = seed_res.json()
            assert seed_data["seeded_count"] == 6

            # 3. Verify history aggregation
            hist_res = await client.get("/api/history")
            assert hist_res.status_code == 200
            hist_data = hist_res.json()
            assert hist_data["stats"]["total_tabs"] == 6
            assert hist_data["stats"]["total_minutes_saved"] > 0
            assert len(hist_data["items"]) == 6

            # 4. Filter by verdict
            read_res = await client.get("/api/history?filter_verdict=Read")
            assert read_res.status_code == 200
            for item in read_res.json()["items"]:
                assert item["sloth_verdict"] == "Read"

    asyncio.run(_test())


def test_digest_direct_content():
    async def _test():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {
                "title": "Autonomous AI Agents in Cloud Native Architecture",
                "content": """
                Autonomous AI agents deployed on modern cloud platforms like Render enable self-healing,
                zero-configuration daemon workers that summarize data, process webhooks, and orchestrate
                microservices without manual developer intervention.
                """
            }
            res = await client.post("/api/digest", json=payload)
            assert res.status_code == 200
            data = res.json()
            assert "id" in data
            assert data["sloth_verdict"] in ["Read", "Skim", "Skip"]
            assert len(data["two_line_brief"]) > 10
            assert data["metrics"]["time_saved_minutes"] >= 0

    asyncio.run(_test())
