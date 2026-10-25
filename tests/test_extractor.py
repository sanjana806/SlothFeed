"""Unit tests for SlothFeed article extractor and clutter stripper."""

import pytest
from backend.extractor import (
    clean_html,
    calculate_reading_time,
    clean_raw_text,
    extract_domain,
    extract_title_from_html
)


def test_calculate_reading_time():
    assert calculate_reading_time(0) == 0
    assert calculate_reading_time(100) == 1
    assert calculate_reading_time(200) == 1
    assert calculate_reading_time(400) == 2
    assert calculate_reading_time(1000) == 5


def test_clean_html_strips_scripts_and_nav():
    messy_html = """
    <html>
      <head><title>Test Article - TechBlog</title></head>
      <body>
        <nav><a href="/home">Home</a><a href="/login">Sign In</a></nav>
        <script>console.log("tracking pixel");</script>
        <style>.ad-banner { display: block; }</style>
        <article>
          <h1>Deep Learning on Edge Hardware</h1>
          <p>Running models locally preserves user privacy and eliminates cloud inference fees.</p>
        </article>
        <footer>Copyright 2026 TechBlog</footer>
      </body>
    </html>
    """
    cleaned = clean_html(messy_html)
    assert "Home" not in cleaned
    assert "tracking pixel" not in cleaned
    assert ".ad-banner" not in cleaned
    assert "Running models locally preserves user privacy" in cleaned
    assert "Copyright" not in cleaned


def test_extract_title():
    raw_html = "<html><head><title>Why Gemma 2 Wins - DeepMind Blog</title></head><body></body></html>"
    title = extract_title_from_html(raw_html)
    assert title == "Why Gemma 2 Wins"


def test_extract_domain():
    assert extract_domain("https://www.render.com/docs/blueprints") == "render.com"
    assert extract_domain("https://deepmind.google/gemma") == "deepmind.google"
    assert extract_domain("not-a-valid-url") == "" or extract_domain("not-a-valid-url") == "direct-input"


def test_clean_raw_text():
    raw = "Here is a quick thought about cloud architecture and Render blueprints."
    res = clean_raw_text(raw, custom_title="Cloud Architecture")
    assert res["success"] is True
    assert res["title"] == "Cloud Architecture"
    assert res["word_count"] == 11
    assert res["reading_time_minutes"] == 1
