"""
Animation Industry News Fetcher
Real-time RSS feed aggregation from 14 animation industry sources.
Usage: python fetch_news.py [--category CAT] [--source SRC] [--search TERM] [--limit N] [--date YYYY-MM-DD] [--list-categories] [--list-sources]
Output: JSON to stdout
"""

import sys
import json
import argparse
import hashlib
import concurrent.futures
from datetime import datetime
from typing import Optional


def ensure_deps():
    """Auto-install missing dependencies."""
    deps = {
        "feedparser": "feedparser",
        "httpx": "httpx",
        "bs4": "beautifulsoup4",
    }
    missing = []
    for mod, pkg in deps.items():
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)
    if missing:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q"] + missing)
        # Re-import after install
        for mod in deps:
            try:
                __import__(mod)
            except ImportError:
                pass


ensure_deps()

import feedparser
import httpx
from bs4 import BeautifulSoup


# ─── RSS Feed Sources (14 sources from anymationnation_news) ───
RSS_FEEDS: list[dict] = [
    {"url": "https://www.cartoonbrew.com/feed", "name": "Cartoon Brew", "category": "industry_news", "website": "https://www.cartoonbrew.com"},
    {"url": "https://www.awn.com/rss.xml", "name": "Animation World Network", "category": "industry_news", "website": "https://www.awn.com"},
    {"url": "https://motionographer.com/feed/", "name": "Motionographer", "category": "motion_design", "website": "https://motionographer.com"},
    {"url": "https://www.animationmagazine.net/feed/", "name": "Animation Magazine", "category": "industry_news", "website": "https://www.animationmagazine.net"},
    {"url": "https://www.reddit.com/r/animation/.rss", "name": "Reddit r/animation", "category": "community", "website": "https://www.reddit.com/r/animation"},
    {"url": "https://www.reddit.com/r/animationcareer/.rss", "name": "Reddit r/animationcareer", "category": "careers", "website": "https://www.reddit.com/r/animationcareer"},
    {"url": "https://www.reddit.com/r/blender/.rss", "name": "Reddit r/blender", "category": "3d_animation", "website": "https://www.reddit.com/r/blender"},
    {"url": "https://www.reddit.com/r/MotionDesign/.rss", "name": "Reddit r/MotionDesign", "category": "motion_design", "website": "https://www.reddit.com/r/MotionDesign"},
    {"url": "https://www.skwigly.co.uk/feed/", "name": "Skwigly", "category": "industry_news", "website": "https://www.skwigly.co.uk"},
    {"url": "https://blog.animationstudies.org/?feed=rss2", "name": "Animation Studies", "category": "academic", "website": "https://blog.animationstudies.org"},
    {"url": "https://stopmotionmagazine.com/feed/", "name": "Stop Motion Magazine", "category": "industry_news", "website": "https://stopmotionmagazine.com"},
    {"url": "https://www.animationworld.net/feed/", "name": "Animation World", "category": "industry_news", "website": "https://www.animationworld.net"},
    {"url": "https://europeananimationjournal.com/feed/", "name": "European Animation Journal", "category": "industry_news", "website": "https://www.europeananimationjournal.com"},
    {"url": "https://www.stashmedia.tv/feed/", "name": "Stash Media", "category": "motion_design", "website": "https://www.stashmedia.tv"},
]

CATEGORY_LABELS: dict[str, str] = {
    "industry_news": "行业新闻",
    "motion_design": "动态设计",
    "community": "社区讨论",
    "careers": "职业发展",
    "3d_animation": "3D 动画",
    "academic": "学术研究",
}

SOURCE_WEBSITES: dict[str, str] = {f["name"]: f["website"] for f in RSS_FEEDS}
FEED_BY_NAME: dict[str, dict] = {f["name"]: f for f in RSS_FEEDS}


def hash_url(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def fetch_single_feed(feed_config: dict) -> tuple[dict, list[dict], Optional[str]]:
    """Fetch a single RSS feed. Returns (feed_config, articles, error)."""
    try:
        resp = httpx.get(
            feed_config["url"],
            headers={"User-Agent": "AnimationNewsAggregator/1.0"},
            timeout=30.0,
            follow_redirects=True,
        )
        resp.raise_for_status()

        feed = feedparser.parse(resp.text)
        articles = []

        for entry in feed.entries:
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                published = datetime(*entry.updated_parsed[:6])

            summary = ""
            if hasattr(entry, "summary"):
                soup = BeautifulSoup(entry.summary, "html.parser")
                summary = soup.get_text()[:500].strip()

            articles.append({
                "title": entry.get("title", "No Title"),
                "url": entry.get("link", ""),
                "source": feed_config["name"],
                "category": feed_config["category"],
                "summary": summary,
                "published_at": published.isoformat() if published else None,
            })

        return (feed_config, articles, None)
    except Exception as e:
        return (feed_config, [], str(e))


def fetch_all_feeds(category: Optional[str] = None, source: Optional[str] = None) -> list[dict]:
    """Fetch feeds in parallel, optionally filtered by category or source."""
    feeds_to_fetch = RSS_FEEDS
    if category:
        feeds_to_fetch = [f for f in feeds_to_fetch if f["category"] == category]
    if source:
        feeds_to_fetch = [f for f in feeds_to_fetch if f["name"] == source]

    all_articles: list[dict] = []
    seen_hashes: set[str] = set()
    errors: list[str] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_single_feed, f): f for f in feeds_to_fetch}
        for future in concurrent.futures.as_completed(futures):
            feed_config, articles, error = future.result()
            if error:
                errors.append(f"{feed_config['name']}: {error}")
            else:
                for article in articles:
                    h = hash_url(article["url"])
                    if h not in seen_hashes:
                        seen_hashes.add(h)
                        all_articles.append(article)

    # Sort by published_at descending
    all_articles.sort(
        key=lambda a: a["published_at"] or "",
        reverse=True,
    )
    return all_articles


def filter_articles(
    articles: list[dict],
    search: Optional[str] = None,
    date: Optional[str] = None,
    limit: int = 20,
) -> list[dict]:
    """Apply search, date filter, and limit to articles."""
    result = articles

    if search:
        term = search.lower()
        result = [
            a for a in result
            if term in a["title"].lower() or term in (a["summary"] or "").lower()
        ]

    if date:
        result = [a for a in result if (a["published_at"] or "").startswith(date)]

    return result[:limit]


def list_categories() -> list[dict]:
    """List all categories with source counts."""
    counts: dict[str, int] = {}
    for f in RSS_FEEDS:
        counts[f["category"]] = counts.get(f["category"], 0) + 1
    return [
        {"category": cat, "label": CATEGORY_LABELS.get(cat, cat), "source_count": cnt}
        for cat, cnt in sorted(counts.items())
    ]


def list_sources() -> list[dict]:
    """List all RSS feed sources with categories."""
    return [
        {
            "name": f["name"],
            "category": f["category"],
            "category_label": CATEGORY_LABELS.get(f["category"], f["category"]),
            "website": f["website"],
        }
        for f in RSS_FEEDS
    ]


def cmd_fetch_news(args):
    """Fetch animation news."""
    articles = fetch_all_feeds(category=args.category, source=args.source)
    result = filter_articles(articles, search=args.search, date=args.date, limit=args.limit)
    print(json.dumps({
        "count": len(result),
        "total_fetched": len(articles),
        "articles": result,
    }, ensure_ascii=False, indent=2))


def cmd_brief_news(args):
    """Fetch animation news in aihot-style Markdown brief format."""
    from datetime import timezone as dt_timezone, timedelta as dt_timedelta

    articles = fetch_all_feeds(category=args.category, source=args.source)
    result = filter_articles(articles, search=args.search, date=args.date, limit=args.limit)

    # ---- Time formatting ----
    beijing_tz = dt_timezone(dt_timedelta(hours=8))
    now = datetime.now(beijing_tz)

    def rel_time(iso_str):
        if not iso_str:
            return ""
        try:
            dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00")).astimezone(beijing_tz)
            diff = now - dt
            if diff < dt_timedelta(minutes=1):
                return "刚刚"
            elif diff < dt_timedelta(hours=1):
                return f"{max(1, int(diff.total_seconds() / 60))} 分钟前"
            elif diff < dt_timedelta(hours=24):
                return f"{int(diff.total_seconds() / 3600)} 小时前"
            elif diff < dt_timedelta(days=2):
                return "昨天"
            elif diff < dt_timedelta(days=8):
                return f"{int(diff.total_seconds() / 86400)} 天前"
            else:
                return dt.strftime("%m/%d")
        except Exception:
            return iso_str

    # ---- Quality filtering: skip low-signal Reddit posts ----
    LOW_SIGNAL_KEYWORDS = ["submitted by", "[link] [comments]", "No Title"]
    def is_low_signal(article):
        if article.get("source", "").startswith("Reddit"):
            summary = article.get("summary", "")
            if not summary or all(kw in summary for kw in LOW_SIGNAL_KEYWORDS if kw in summary):
                return True
            # Very short Reddit posts with no real content
            if len(summary) < 50:
                return True
        return False

    brief_articles = [a for a in result if not is_low_signal(a)]

    # ---- Category grouping (aihot-style Chinese labels) ----
    BRIEF_CATEGORIES = [
        ("film_tv", "动画电影 / 剧集", ["industry_news"]),
        ("industry", "行业动态", ["industry_news"]),
        ("tech_tools", "制作技术 / 工具", ["motion_design"]),
        ("community", "社区话题", ["community", "careers", "3d_animation", "academic", "motion_design"]),
    ]

    # Build category index: article_index -> category display info
    # A single article may match multiple categories (e.g. industry_news can be film_tv or industry)
    # We assign to the first matching category
    article_cat_idx: dict[int, tuple[str, str]] = {}

    for idx, a in enumerate(brief_articles):
        cat = a.get("category", "")
        for brief_key, brief_label, match_cats in BRIEF_CATEGORIES:
            if cat in match_cats:
                # For industry_news, try heuristic: if title mentions film/movie/boxoffice/season/series → film_tv
                if cat == "industry_news" and brief_key == "film_tv":
                    title_lower = a.get("title", "").lower()
                    if any(kw in title_lower for kw in [
                        "film", "movie", "short", "season", "box office",
                        "feature", "trailer", "episode", "tv", "series",
                        "anime", "续作", "票房", "第一季", "第二季",
                        "cour", "frame", "work in progress", "续订",
                        "annecy",
                    ]):
                        article_cat_idx[idx] = (brief_key, brief_label)
                        break
                elif cat == "industry_news" and brief_key == "industry":
                    article_cat_idx[idx] = (brief_key, brief_label)
                    break
                elif cat != "industry_news":
                    article_cat_idx[idx] = (brief_key, brief_label)
                    break

    # Group articles by display category, preserving order
    grouped: dict[str, list[tuple[int, dict]]] = {}
    for idx, a in enumerate(brief_articles):
        if idx in article_cat_idx:
            bk = article_cat_idx[idx][1]
            grouped.setdefault(bk, []).append((idx, a))

    # ---- Output Markdown ----
    print(f"**动画行业动态 — 过去 24 小时**\n")
    print(f"数据来自 {len(RSS_FEEDS)} 个行业 RSS 源")
    print()

    global_num = 0
    for brief_key, brief_label, _ in BRIEF_CATEGORIES:
        entries = grouped.get(brief_label, [])
        if not entries:
            continue
        print(f"## {brief_label}")
        print()
        for idx, a in entries:
            global_num += 1
            title = a.get("title", "No Title")
            source = a.get("source", "")
            url = a.get("url", "")
            summary = a.get("summary", "")
            pub = rel_time(a.get("published_at", ""))
            # Trim summary
            if len(summary) > 120:
                summary = summary[:120].rsplit(" ", 1)[0] + "…"
            elif summary.endswith("…") or summary.endswith("..."):
                pass
            print(f"{global_num}. **{title}**")
            print(f"   {pub} · {source}")
            if summary:
                print(f"   {summary}")
            print(f"   {url}")
            print()
        print()


def cmd_list_categories(args):
    print(json.dumps({"categories": list_categories()}, ensure_ascii=False, indent=2))


def cmd_list_sources(args):
    print(json.dumps({"sources": list_sources()}, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Animation Industry News Fetcher")
    sub = parser.add_subparsers(dest="command")

    fetch_p = sub.add_parser("fetch", help="Fetch animation news")
    fetch_p.add_argument("--category", "-c", choices=list(CATEGORY_LABELS.keys()), help="Filter by category")
    fetch_p.add_argument("--source", "-s", help="Filter by source name")
    fetch_p.add_argument("--search", "-q", help="Search in title and summary")
    fetch_p.add_argument("--date", "-d", help="Filter by date (YYYY-MM-DD)")
    fetch_p.add_argument("--limit", "-n", type=int, default=20, help="Max articles (default: 20)")
    fetch_p.set_defaults(func=cmd_fetch_news)

    brief_p = sub.add_parser("brief", help="Output news in aihot-style Markdown brief format")
    brief_p.add_argument("--category", "-c", choices=list(CATEGORY_LABELS.keys()), help="Filter by category")
    brief_p.add_argument("--source", "-s", help="Filter by source name")
    brief_p.add_argument("--search", "-q", help="Search in title and summary")
    brief_p.add_argument("--date", "-d", help="Filter by date (YYYY-MM-DD)")
    brief_p.add_argument("--limit", "-n", type=int, default=20, help="Max articles (default: 20)")
    brief_p.set_defaults(func=cmd_brief_news)

    cat_p = sub.add_parser("categories", help="List all categories")
    cat_p.set_defaults(func=cmd_list_categories)

    src_p = sub.add_parser("sources", help="List all sources")
    src_p.set_defaults(func=cmd_list_sources)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
