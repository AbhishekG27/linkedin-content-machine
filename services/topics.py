"""Trending topics: Tavily web search (recent day/month) + optional OpenAI to structure."""
from typing import List, Dict, Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import TAVILY_API_KEY

DEFAULT_NICHES = (
    "AI, Gen AI, Agentic AI, VLSI, Embedded Systems, IT Services and Industry"
)


def search_trending_topics(
    niche: str = DEFAULT_NICHES,
    count: int = 10,
    recency: str = "month",  # "day" | "week" | "month"
) -> List[Dict[str, Any]]:
    """
    Use Tavily web search (Google-like) with time filter for recent topics.
    Returns list of dicts with keys: title, reason, summary.
    recency: "day" (today), "week", or "month".
    """
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY is not set in .env")

    try:
        from tavily import TavilyClient
    except ImportError:
        raise ImportError("Install tavily-python: pip install tavily-python")

    client = TavilyClient(api_key=TAVILY_API_KEY)
    time_range = recency if recency in ("day", "week", "month", "year") else "month"

    # Search for recent news/trends in the niche (Tavily = web/Google-like search)
    query = (
        f"trending topics and news for LinkedIn content in {niche} "
        f"published or updated in the last {time_range}"
    )
    response = client.search(
        query=query,
        search_depth="basic",
        topic="news",
        time_range=time_range,
        max_results=min(count + 5, 20),
    )
    results = getattr(response, "results", []) or []
    if isinstance(response, dict):
        results = response.get("results", [])

    # Map search results to topic format
    seen_titles = set()
    topics = []
    for r in results:
        title = (getattr(r, "title", None) or (r.get("title") if isinstance(r, dict) else None) or "").strip()
        content = (getattr(r, "content", None) or (r.get("content") if isinstance(r, dict) else None) or "").strip()
        if not title or len(title) < 3:
            continue
        if title.lower() in seen_titles:
            continue
        seen_titles.add(title.lower())
        reason = f"Recent ({time_range}) from web search."
        summary = (content[:300] + "…") if len(content) > 300 else content
        topics.append({
            "title": title[:200],
            "reason": reason[:300],
            "summary": summary[:300],
        })
        if len(topics) >= count:
            break

    # If Tavily returned few results, optionally run a second query (broader)
    if len(topics) < count and count > 0:
        query2 = f"latest news and trends {niche} this month"
        try:
            response2 = client.search(
                query=query2,
                search_depth="basic",
                topic="general",
                time_range=time_range,
                max_results=min(count + 5, 20),
            )
            res2 = getattr(response2, "results", []) or []
            if isinstance(response2, dict):
                res2 = response2.get("results", [])
            for r in res2:
                if len(topics) >= count:
                    break
                title = (getattr(r, "title", None) or (r.get("title") if isinstance(r, dict) else None) or "").strip()
                content = (getattr(r, "content", None) or (r.get("content") if isinstance(r, dict) else None) or "").strip()
                if not title or title.lower() in seen_titles:
                    continue
                seen_titles.add(title.lower())
                topics.append({
                    "title": title[:200],
                    "reason": f"Recent ({time_range}) from web search.",
                    "summary": (content[:300] + "…") if len(content) > 300 else content[:300],
                })
        except Exception:
            pass

    # Add index
    for i, t in enumerate(topics[:count], 1):
        t["index"] = i
    return topics[:count]
