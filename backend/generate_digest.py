#!/usr/bin/env python3
"""
generate_digest.py — Morning news digest pipeline.

Fetches cybersecurity RSS feeds and secondary news from Currents API,
summarises each article with Gemini, and writes digest.json for the frontend.
"""

import argparse
import hashlib
import json
import logging
import os
import re
import socket
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Enforce 25-second socket timeout globally to prevent any TCP hang
socket.setdefaulttimeout(25)

import feedparser
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("digest")

# ── Constants ────────────────────────────────────────────────────────────────
RSS_FEEDS = {
    "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
    "SecurityWeek": "https://www.securityweek.com/feed/",
    "Krebs on Security": "https://krebsonsecurity.com/feed/",
    "CISA Advisories": "https://www.cisa.gov/cybersecurity-advisories/all.xml",
    "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
}

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

CVE_RE = re.compile(r"CVE-\d{4}-\d{4,7}")

OUTPUT_PATH = Path(
    os.getenv(
        "DIGEST_OUTPUT_PATH",
        Path(__file__).resolve().parent.parent / "frontend" / "public" / "digest.json",
    )
)

CURRENTS_API_URL = "https://api.currentsapi.services/v1/latest-news"
CURRENTS_CATEGORIES = ["technology", "business", "world"]

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


# ── Helpers ──────────────────────────────────────────────────────────────────
def _article_id(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


def _normalize_url(url: str) -> str:
    """Strip trailing slashes and query params for dedup."""
    url = url.strip().rstrip("/")
    return url.split("?")[0].split("#")[0]


def _is_valid_image_url(url: str | None) -> bool:
    """Validate that URL looks like a real image and not a tracking pixel."""
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        return False
    lower = url.lower()
    # Skip common 1x1 tracking beacons / feedburner tracking gifs
    if "feedburner.com/~r/" in lower or "1x1" in lower or "/tracking" in lower:
        return False
    return True


def _extract_image_url(entry) -> str | None:
    """Try multiple sources for an article cover image."""
    # 1. media:content
    media = entry.get("media_content") or []
    for m in media:
        url = m.get("url")
        if _is_valid_image_url(url):
            return url.strip()

    # 2. media:thumbnail
    thumbnails = entry.get("media_thumbnail") or []
    for t in thumbnails:
        url = t.get("url")
        if _is_valid_image_url(url):
            return url.strip()

    # 3. enclosure
    enclosures = entry.get("enclosures") or []
    for enc in enclosures:
        url = enc.get("href") or enc.get("url")
        enc_type = (enc.get("type") or "").lower()
        if _is_valid_image_url(url) and ("image" in enc_type or any(url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"])):
            return url.strip()

    # 4. embedded <img> in summary/content HTML
    for field in ("content", "summary_detail", "summary", "description"):
        raw_html = ""
        val = entry.get(field)
        if isinstance(val, list) and val:
            raw_html = val[0].get("value", "")
        elif isinstance(val, dict):
            raw_html = val.get("value", "")
        elif isinstance(val, str):
            raw_html = val

        if "<img" in raw_html:
            try:
                soup = BeautifulSoup(raw_html, "html.parser")
                for img in soup.find_all("img"):
                    src = img.get("src")
                    # skip tracking pixels
                    width = img.get("width")
                    height = img.get("height")
                    if width in ("1", 1, "0", 0) or height in ("1", 1, "0", 0):
                        continue
                    if _is_valid_image_url(src):
                        return src.strip()
            except Exception:
                pass

    return None


def _extract_image_via_trafilatura(url: str) -> str | None:
    """Fetch page and use trafilatura to pull og:image."""
    try:
        import trafilatura

        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            meta = trafilatura.extract_metadata(downloaded)
            if meta and meta.image and _is_valid_image_url(meta.image):
                return meta.image.strip()
    except Exception:
        pass
    return None


def _extract_text(entry, url: str) -> str:
    """Get clean article text — trafilatura first, BS4 fallback."""
    try:
        import trafilatura

        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            if text and len(text) > 100:
                return text
    except Exception as exc:
        log.debug("trafilatura failed for %s: %s", url, exc)

    # Fallback: clean the RSS summary with BeautifulSoup
    raw = entry.get("summary") or entry.get("description") or ""
    return BeautifulSoup(raw, "html.parser").get_text(separator=" ", strip=True)


def _parse_published(entry) -> datetime | None:
    """Parse entry published date into an aware datetime."""
    import email.utils
    import time

    for attr in ("published_parsed", "updated_parsed"):
        tp = entry.get(attr)
        if tp:
            try:
                return datetime(*tp[:6], tzinfo=timezone.utc)
            except Exception:
                pass

    for attr in ("published", "updated"):
        raw = entry.get(attr)
        if raw:
            try:
                parsed = email.utils.parsedate_to_datetime(raw)
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                return parsed
            except Exception:
                pass
    return None


# ── RSS fetch ────────────────────────────────────────────────────────────────
def fetch_rss_articles() -> list[dict]:
    """Fetch and parse all cybersecurity RSS feeds."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    seen_urls: set[str] = set()
    articles: list[dict] = []

    for source_name, feed_url in RSS_FEEDS.items():
        log.info("Fetching %s …", source_name)
        try:
            # Use requests with browser headers first to avoid 403 blocks
            resp = requests.get(
                feed_url,
                headers={
                    "User-Agent": BROWSER_UA,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                },
                timeout=15,
            )
            if resp.status_code == 200:
                feed = feedparser.parse(resp.content)
            else:
                feed = feedparser.parse(feed_url, agent=BROWSER_UA)
        except Exception as exc:
            log.warning("requests fetch failed for %s, falling back to feedparser: %s", source_name, exc)
            try:
                feed = feedparser.parse(feed_url, agent=BROWSER_UA)
            except Exception as e2:
                log.error("Failed to fetch %s: %s", source_name, e2)
                continue

        for entry in feed.entries:
            url = entry.get("link") or ""
            norm = _normalize_url(url)
            if not norm or norm in seen_urls:
                continue

            pub_dt = _parse_published(entry)
            if pub_dt and pub_dt < cutoff:
                continue

            seen_urls.add(norm)

            # Image: RSS sources first, then trafilatura
            image_url = _extract_image_url(entry)
            if not image_url:
                image_url = _extract_image_via_trafilatura(url)

            # Text
            text = _extract_text(entry, url)

            # CVEs
            cve_ids = sorted(set(CVE_RE.findall(text + " " + (entry.get("title") or ""))))

            articles.append(
                {
                    "url": url,
                    "norm_url": norm,
                    "category": "Cybersecurity",
                    "source": source_name,
                    "title": entry.get("title", "Untitled"),
                    "text": text[:3000],  # cap for Gemini context
                    "image_url": image_url,
                    "published_at": (
                        pub_dt.strftime("%Y-%m-%dT%H:%M:%SZ") if pub_dt else None
                    ),
                    "cve_ids": cve_ids,
                }
            )

    log.info("RSS: %d articles after dedup + 24h filter", len(articles))
    return articles


# ── Currents API ─────────────────────────────────────────────────────────────
def fetch_currents_articles() -> list[dict]:
    """Fetch secondary categories from Currents API."""
    api_key = os.getenv("CURRENTS_API_KEY")
    if not api_key:
        log.warning("CURRENTS_API_KEY not set — skipping secondary categories")
        return []

    articles: list[dict] = []
    seen: set[str] = set()

    for category in CURRENTS_CATEGORIES:
        log.info("Fetching Currents API — %s …", category)
        try:
            resp = requests.get(
                CURRENTS_API_URL,
                params={"apiKey": api_key, "category": category, "language": "en"},
                headers={"User-Agent": BROWSER_UA},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            log.error("Currents API error (%s): %s", category, exc)
            continue

        for item in data.get("news", []):
            url = item.get("url", "")
            norm = _normalize_url(url)
            if not norm or norm in seen:
                continue
            seen.add(norm)

            img = item.get("image")
            if img in (None, "None", ""):
                img = None

            articles.append(
                {
                    "url": url,
                    "norm_url": norm,
                    "category": category.capitalize(),
                    "source": "Currents API",
                    "title": item.get("title", "Untitled"),
                    "text": (item.get("description") or "")[:3000],
                    "image_url": img,
                    "published_at": item.get("published"),
                    "cve_ids": [],
                }
            )

    log.info("Currents: %d articles", len(articles))
    return articles


# ── Gemini summariser ────────────────────────────────────────────────────────
def _build_summarise_prompt(article: dict) -> str:
    return f"""You are a concise news digest writer. Summarise this article as JSON.

**Rules**
- "hook": exactly 1 sentence, ≤ 20 words.
- "bullets": array of exactly 2 strings, each ≤ 15 words.
- "why_it_matters": exactly 1 sentence.
- "read_time_sec": estimated read time in seconds (integer).

Return ONLY valid JSON (no markdown fences) with keys: hook, bullets, why_it_matters, read_time_sec.

---
Title: {article['title']}
Source: {article['source']}
Text: {article['text'][:2000]}
"""


def summarise_articles(articles: list[dict]) -> list[dict]:
    """Call Gemini to summarise each article, return enriched dicts."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        log.error("GEMINI_API_KEY not set — cannot summarise")
        return []

    from google import genai
    from google.genai import types

    # Enforce 20s timeout per API call so no slow response can hang the runner
    client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=20_000))

    results: list[dict] = []
    for i, article in enumerate(articles, 1):
        log.info("Summarising %d/%d: %s", i, len(articles), article["title"][:60])
        try:
            resp = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=_build_summarise_prompt(article),
            )
            raw = resp.text.strip()
            # Strip markdown fences if model returns them anyway
            if raw.startswith("```"):
                raw = re.sub(r"^```(?:json)?\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)
            summary = json.loads(raw)
        except Exception as exc:
            log.warning("Gemini failed for '%s': %s", article["title"][:40], exc)
            summary = {
                "hook": article["title"],
                "bullets": ["See full article for details", "Link below"],
                "why_it_matters": "Read the full article for context.",
                "read_time_sec": 180,
            }

        results.append(
            {
                "id": _article_id(article["url"]),
                "category": article["category"],
                "source": article["source"],
                "title": article["title"],
                "hook": summary.get("hook", article["title"]),
                "bullets": summary.get("bullets", [])[:2],
                "why_it_matters": summary.get("why_it_matters", ""),
                "read_time_sec": summary.get("read_time_sec", 180),
                "image_url": article["image_url"],
                "full_article_url": article["url"],
                "published_at": article["published_at"],
                "cve_ids": article["cve_ids"],
                "saved": False,
            }
        )

    return results


# ── ntfy push ────────────────────────────────────────────────────────────────
def send_ntfy_notification(articles: list[dict]) -> None:
    """Push top cybersecurity headline to ntfy.sh."""
    topic = os.getenv("NTFY_TOPIC")
    if not topic:
        log.info("NTFY_TOPIC not set — skipping push notification")
        return

    cyber = [a for a in articles if a.get("category") == "Cybersecurity"]
    top = cyber[0] if cyber else (articles[0] if articles else None)
    if not top:
        log.info("No articles to push")
        return

    app_link = os.getenv("APP_URL", top["full_article_url"])
    try:
        payload = f"{top['title']}\n\n{top['hook']}"
        resp = requests.post(
            f"https://ntfy.sh/{topic}",
            data=payload.encode("utf-8"),
            headers={
                "Title": f"☕ Morning Cyber: {top['title'][:50]}",
                "Click": app_link,
                "Tags": "shield,newspaper,coffee",
                "Priority": "default",
            },
            timeout=10,
        )
        resp.raise_for_status()
        log.info("ntfy notification sent to topic '%s' for: %s", topic, top["title"][:60])
    except Exception as exc:
        log.error("ntfy push failed: %s", exc)


# ── Output & Weekly Recap ────────────────────────────────────────────────────
def build_weekly_recap(articles: list[dict]) -> dict:
    """Group top articles by category and assign impact/viral badges."""
    categories = ["Cybersecurity", "Technology", "Business", "World"]
    recap = {}

    for cat in categories:
        cat_articles = [a for a in articles if a.get("category") == cat]
        if cat == "Cybersecurity":
            cat_articles.sort(
                key=lambda a: (len(a.get("cve_ids", [])), a.get("read_time_sec", 0)),
                reverse=True,
            )
        else:
            cat_articles.sort(key=lambda a: a.get("read_time_sec", 0), reverse=True)

        selected = []
        for rank, a in enumerate(cat_articles[:3], 1):
            item = dict(a)
            if a.get("cve_ids"):
                badge = f"🔥 {a['cve_ids'][0]} Critical"
            elif rank == 1:
                badge = f"🔥 Top {cat} Story"
            elif rank == 2:
                badge = "⚡ Viral Discussion"
            else:
                badge = "📌 High Impact"
            item["viral_badge"] = badge
            item["viral_rank"] = rank
            item["impact_summary"] = a.get("why_it_matters") or a.get("hook", "")
            selected.append(item)
        recap[cat] = selected

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "title": "Weekly Intelligence & Viral Roundup",
        "period": "Last 7 Days",
        "categories": recap,
    }


def write_digest(articles: list[dict], weekly_recap: dict | None = None) -> None:
    """Write final digest.json including weekly top stories recap."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    digest = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "articles": articles,
        "weekly_recap": weekly_recap or build_weekly_recap(articles),
    }
    OUTPUT_PATH.write_text(json.dumps(digest, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("Wrote %d articles + weekly recap to %s", len(articles), OUTPUT_PATH)


# ── Mock mode ────────────────────────────────────────────────────────────────
def run_mock(notify: bool = False) -> None:
    """Generate realistic mock digest.json without any network calls."""
    from mock_data import generate_mock_articles, generate_mock_weekly_recap

    articles = generate_mock_articles()
    weekly_recap = generate_mock_weekly_recap(articles)
    write_digest(articles, weekly_recap=weekly_recap)
    log.info("Mock digest generated with %d articles and weekly recap", len(articles))
    if notify:
        send_ntfy_notification(articles)


# ── Live mode ────────────────────────────────────────────────────────────────
def run_live() -> None:
    """Full pipeline: fetch → summarise → write → notify."""
    rss_articles = fetch_rss_articles()
    currents_articles = fetch_currents_articles()

    all_raw = rss_articles + currents_articles

    if not all_raw:
        log.warning("No articles fetched — writing empty digest")
        write_digest([])
        return

    # Deduplicate across both sources by normalised URL
    seen: set[str] = set()
    deduped: list[dict] = []
    for a in all_raw:
        if a["norm_url"] not in seen:
            seen.add(a["norm_url"])
            deduped.append(a)

    log.info("Total after cross-source dedup: %d articles", len(deduped))

    # Summarise with Gemini
    enriched = summarise_articles(deduped)

    if not enriched:
        log.warning("Summarisation produced no results — writing raw fallback")
        # Produce a basic digest without AI summaries
        enriched = []
        for a in deduped:
            enriched.append(
                {
                    "id": _article_id(a["url"]),
                    "category": a["category"],
                    "source": a["source"],
                    "title": a["title"],
                    "hook": a["title"],
                    "bullets": ["See full article for details", "Link below"],
                    "why_it_matters": "Read the full article for context.",
                    "read_time_sec": 180,
                    "image_url": a["image_url"],
                    "full_article_url": a["url"],
                    "published_at": a["published_at"],
                    "cve_ids": a["cve_ids"],
                    "saved": False,
                }
            )

    write_digest(enriched)
    send_ntfy_notification(enriched)


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate morning news digest")
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Skip all network calls and write realistic mock data",
    )
    parser.add_argument(
        "--notify",
        action="store_true",
        help="Trigger ntfy push notification (useful with --mock testing)",
    )
    args = parser.parse_args()

    try:
        if args.mock:
            run_mock(notify=args.notify)
        else:
            run_live()
    except Exception as exc:
        log.exception("Fatal error: %s", exc)
        sys.exit(1)
