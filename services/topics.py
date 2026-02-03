"""Trending topics: Tavily web research + Gemini to shape topics per strategist brief (Agentic AI, Gen AI, AI, Embedded, VLSI)."""
import json
import re
from typing import List, Dict, Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import TAVILY_API_KEY, GEMINI_API_KEY, GEMINI_CHAT_MODEL

DEFAULT_NICHES = (
    "AI, Gen AI, Agentic AI, VLSI, Embedded Systems, IT Services and Industry"
)

TOPIC_STRATEGIST_SYSTEM = """You are a social media content strategist and growth marketer.
Use Tavily-powered web research to gather recent, credible, and high-engagement information related to Agentic AI, Gen AI, AI, Embedded System, VLSI.

Research Instructions:
- Prioritize credible blogs, industry reports, expert opinions, trending social posts, and news
- Extract statistics, strong opinions, contrarian takes, and emerging trends
- Identify what is currently resonating on LinkedIn

Content Scope (rotate across topics):
- Artificial Intelligence (AI)
- Generative AI
- Agentic AI & autonomous systems
- VLSI & semiconductor innovation
- Embedded Systems
- IT Services & digital transformation
- Industry & workforce evolution

Tone: enterprise credibility, strategic clarity, future-readiness. Avoid speculative or clickbait-only claims; prioritize data-backed insights."""


def search_trending_topics(
    niche: str = DEFAULT_NICHES,
    count: int = 10,
    recency: str = "month",
) -> List[Dict[str, Any]]:
    """
    Use Tavily for web research, then Gemini to shape topics per strategist brief.
    Returns list of dicts with keys: title, reason, summary.
    """
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY is not set in .env")

    try:
        from tavily import TavilyClient
    except ImportError:
        raise ImportError("Install tavily-python: pip install tavily-python")

    client = TavilyClient(api_key=TAVILY_API_KEY)
    time_range = recency if recency in ("day", "week", "month", "year") else "month"

    # Query 1: credible sources + domains (Agentic AI, Gen AI, AI, Embedded, VLSI)
    query1 = (
        f"credible blogs industry reports expert opinions {niche} "
        f"statistics trends LinkedIn trending published last {time_range}"
    )
    response1 = client.search(
        query=query1,
        search_depth="basic",
        topic="general",
        time_range=time_range,
        max_results=min(count + 5, 20),
    )
    results = getattr(response1, "results", []) or []
    if isinstance(response1, dict):
        results = response1.get("results", [])

    # Query 2: domains + trends (if we want more)
    if len(results) < count:
        query2 = (
            f"trends and data {niche} "
            f"digital transformation semiconductor embedded systems AI workforce "
            f"published or updated last {time_range}"
        )
        try:
            response2 = client.search(
                query=query2,
                search_depth="basic",
                topic="news",
                time_range=time_range,
                max_results=min(count + 5, 20),
            )
            res2 = getattr(response2, "results", []) or []
            if isinstance(response2, dict):
                res2 = response2.get("results", [])
            seen_urls = {getattr(r, "url", None) or (r.get("url") if isinstance(r, dict) else "") for r in results}
            for r in res2:
                url = getattr(r, "url", None) or (r.get("url") if isinstance(r, dict) else "")
                if url and url not in seen_urls:
                    results.append(r)
                    seen_urls.add(url)
        except Exception:
            pass

    # Build raw context for Gemini
    raw = []
    for r in results:
        title = (getattr(r, "title", None) or (r.get("title") if isinstance(r, dict) else None) or "").strip()
        content = (getattr(r, "content", None) or (r.get("content") if isinstance(r, dict) else None) or "").strip()
        if title and len(content) > 20:
            raw.append(f"Title: {title}\nSnippet: {content[:400]}")
    raw_text = "\n\n---\n\n".join(raw[:20]) if raw else "No recent results found."

    # If Gemini is available, shape topics with the strategist prompt
    if GEMINI_API_KEY and raw_text.strip():
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(
                GEMINI_CHAT_MODEL,
                system_instruction=TOPIC_STRATEGIST_SYSTEM,
            )
            user_prompt = f"""Based on the following Tavily web search results, output exactly {count} topic ideas for LinkedIn that match the research instructions and content scope above.

Web search results (recent, {time_range}):
{raw_text}

For each topic provide a JSON array of objects with keys: "title", "reason", "summary".
- title: One short, scroll-stopping headline (data-backed, not clickbait).
- reason: Why it fits the domains and what is resonating on LinkedIn (one sentence).
- summary: One-sentence angle or data point for the post.

Return ONLY the JSON array, no other text. Prioritize data-backed insights and what resonates on LinkedIn."""

            resp = model.generate_content(
                user_prompt,
                generation_config={"max_output_tokens": 65536, "temperature": 0.4},
            )
            content = (resp.text or "").strip()
            content_clean = re.sub(r"^```\w*\n?", "", content)
            content_clean = re.sub(r"\n?```\s*$", "", content_clean).strip()
            try:
                topics = json.loads(content_clean)
                if isinstance(topics, list) and len(topics) > 0:
                    result = []
                    for i, t in enumerate(topics[:count], 1):
                        if isinstance(t, dict):
                            result.append({
                                "index": i,
                                "title": str(t.get("title", t))[:200],
                                "reason": str(t.get("reason", ""))[:300],
                                "summary": str(t.get("summary", ""))[:300],
                            })
                        else:
                            result.append({"index": i, "title": str(t)[:200], "reason": "", "summary": ""})
                    return result
            except json.JSONDecodeError:
                pass
        except Exception:
            pass

    # Fallback: use raw Tavily results as topics
    seen_titles = set()
    topics = []
    for r in results:
        title = (getattr(r, "title", None) or (r.get("title") if isinstance(r, dict) else None) or "").strip()
        content = (getattr(r, "content", None) or (r.get("content") if isinstance(r, dict) else None) or "").strip()
        if not title or len(title) < 3 or title.lower() in seen_titles:
            continue
        seen_titles.add(title.lower())
        topics.append({
            "title": title[:200],
            "reason": f"Recent ({time_range}) from Tavily web search; Agentic AI, Gen AI, AI, Embedded, VLSI focus.",
            "summary": (content[:300] + "…") if len(content) > 300 else content[:300],
        })
        if len(topics) >= count:
            break
    for i, t in enumerate(topics[:count], 1):
        t["index"] = i
    return topics[:count]
