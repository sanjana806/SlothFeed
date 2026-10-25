"""
Article Scraper and Clutter Stripper for SlothFeed.
Extracts clean markdown/plain text from web URLs or raw snippets,
stripping ads, navigation, cookie banners, and HTML boilerplate.
"""

import re
import html
import urllib.parse
from typing import Dict, Any, Optional
import httpx

# Fast regex patterns for HTML cleanup
RE_SCRIPT = re.compile(r'<script[^>]*>.*?</script>', re.DOTALL | re.IGNORECASE)
RE_STYLE = re.compile(r'<style[^>]*>.*?</style>', re.DOTALL | re.IGNORECASE)
RE_SVG = re.compile(r'<svg[^>]*>.*?</svg>', re.DOTALL | re.IGNORECASE)
RE_NAV_FOOTER = re.compile(r'<(nav|footer|header|aside|noscript|iframe)[^>]*>.*?</\1>', re.DOTALL | re.IGNORECASE)
RE_TAGS = re.compile(r'<[^>]+>')
RE_WHITESPACE = re.compile(r'[ \t\r\f\v]+')
RE_NEWLINES = re.compile(r'\n{3,}')
RE_TITLE = re.compile(r'<title[^>]*>(.*?)</title>', re.DOTALL | re.IGNORECASE)


def calculate_reading_time(word_count: int, words_per_minute: int = 200) -> int:
    """Calculates estimated reading time in minutes (minimum 1 min for non-empty text)."""
    if word_count <= 0:
        return 0
    return max(1, round(word_count / words_per_minute))


def clean_html(raw_html: str) -> str:
    """Strips HTML clutter, scripts, navigation, and boilerplate."""
    if not raw_html:
        return ""
    
    # Optional trafilatura high-fidelity extraction if installed
    try:
        import trafilatura
        extracted = trafilatura.extract(raw_html, include_links=False, include_images=False)
        if extracted and len(extracted.strip()) > 80:
            return extracted.strip()
    except ImportError:
        pass
    except Exception:
        pass

    # Optional BeautifulSoup fallback if installed
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(raw_html, "html.parser")
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "svg", "iframe"]):
            element.decompose()
        # Find main article or content containers
        article = soup.find("article") or soup.find("main") or soup.find(class_=re.compile(r"content|post|article|entry", re.I)) or soup.body
        if article:
            text = article.get_text(separator="\n")
            text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
            if len(text) > 80:
                return text
    except ImportError:
        pass
    except Exception:
        pass

    # Resilient native regex cleaning fallback (zero external dependency requirement)
    cleaned = RE_SCRIPT.sub(' ', raw_html)
    cleaned = RE_STYLE.sub(' ', cleaned)
    cleaned = RE_SVG.sub(' ', cleaned)
    cleaned = RE_NAV_FOOTER.sub(' ', cleaned)
    cleaned = RE_TAGS.sub(' ', cleaned)
    cleaned = html.unescape(cleaned)
    cleaned = RE_WHITESPACE.sub(' ', cleaned)
    cleaned = RE_NEWLINES.sub('\n\n', cleaned)
    return cleaned.strip()


def extract_title_from_html(raw_html: str, fallback: str = "Untitled Document") -> str:
    """Attempts to extract document title from HTML tags."""
    match = RE_TITLE.search(raw_html)
    if match:
        raw_title = match.group(1).strip()
        cleaned_title = html.unescape(raw_title)
        # Strip common site suffixes like " - Medium" or " | Hacker News"
        cleaned_title = re.split(r'[-–—|•]', cleaned_title)[0].strip()
        if cleaned_title:
            return cleaned_title
    return fallback


def extract_domain(url: str) -> str:
    """Extracts a neat hostname from a URL."""
    try:
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc or "direct-input"
    except Exception:
        return "direct-input"


async def fetch_and_clean_url(url: str, timeout_seconds: float = 8.0) -> Dict[str, Any]:
    """
    Fetches URL content over HTTP and strips web clutter.
    Returns structured article metadata.
    """
    domain = extract_domain(url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SlothFeed/1.0 (Automated Reading Janitor)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            html_content = response.text
            
            title = extract_title_from_html(html_content, fallback=f"Article from {domain}")
            cleaned_text = clean_html(html_content)
            word_count = len(cleaned_text.split())
            reading_time = calculate_reading_time(word_count)

            return {
                "success": True,
                "url": url,
                "domain": domain,
                "title": title,
                "text": cleaned_text,
                "word_count": word_count,
                "reading_time_minutes": reading_time,
                "snippet": cleaned_text[:350] + ("..." if len(cleaned_text) > 350 else "")
            }
    except Exception as exc:
        return {
            "success": False,
            "url": url,
            "domain": domain,
            "title": f"Failed link: {domain}",
            "text": "",
            "error": str(exc),
            "word_count": 0,
            "reading_time_minutes": 0,
            "snippet": f"Could not fetch URL: {str(exc)}"
        }


def clean_raw_text(raw_text: str, custom_title: Optional[str] = None) -> Dict[str, Any]:
    """
    Cleans up pasted text or unformatted blobs.
    """
    cleaned = clean_html(raw_text) if ("<" in raw_text and ">" in raw_text) else raw_text.strip()
    words = cleaned.split()
    word_count = len(words)
    reading_time = calculate_reading_time(word_count)
    
    # Auto-generate a title if none provided
    title = custom_title
    if not title:
        first_line = cleaned.splitlines()[0].strip() if cleaned else "Untitled Thought"
        title = first_line[:80] + ("..." if len(first_line) > 80 else "")

    return {
        "success": True,
        "url": "direct://pasted-content",
        "domain": "pasted-content",
        "title": title,
        "text": cleaned,
        "word_count": word_count,
        "reading_time_minutes": reading_time,
        "snippet": cleaned[:350] + ("..." if len(cleaned) > 350 else "")
    }
