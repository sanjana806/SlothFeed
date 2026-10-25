"""
SlothFeed Asynchronous Background Worker Daemon.
Orchestrated on Render as a dedicated Background Worker service.
Continuously processes background queue / scheduled tab digests without blocking the web tier.
"""

import os
import sys
import time
import signal
import asyncio
import logging

from backend.gemma_runner import GemmaRunner
from backend.mock_data import get_mock_articles
from backend.extractor import clean_raw_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [SlothWorker] %(message)s"
)
logger = logging.getLogger("slothfeed.worker")

RUNNING = True


def handle_shutdown(signum, frame):
    global RUNNING
    logger.info("Shutdown signal received. Finishing current lazy digest and stopping...")
    RUNNING = False


async def run_worker_loop():
    logger.info("Starting SlothFeed Background Daemon on Render...")
    poll_interval = int(os.getenv("WORKER_POLL_INTERVAL", "30"))
    gemma = GemmaRunner()
    logger.info(f"Worker initialized with model: {gemma.model_name} (Mode: {gemma.mode})")

    cycle = 0
    while RUNNING:
        cycle += 1
        logger.info(f"=== Worker Heartbeat Cycle #{cycle} (Polling background ingestion queues) ===")
        
        # Simulate background digestion of incoming webhooks or scheduled feeds
        mock_items = get_mock_articles()
        selected = mock_items[cycle % len(mock_items)]
        logger.info(f"Processing background tab: '{selected['title'][:45]}...'")

        cleaned = clean_raw_text(selected["raw_content"], custom_title=selected["title"])
        digest = await gemma.generate_digest(cleaned["text"], title=cleaned["title"])

        logger.info(
            f"Digest generated successfully: Verdict={digest['sloth_verdict']} | "
            f"Brief='{digest['two_line_brief'][:60]}...'"
        )

        # Rest calmly like a true sloth
        for _ in range(poll_interval):
            if not RUNNING:
                break
            await asyncio.sleep(1)

    logger.info("SlothFeed Background Daemon stopped cleanly.")


def main():
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    asyncio.run(run_worker_loop())


if __name__ == "__main__":
    main()
