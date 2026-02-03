"""OpenAI ChatGPT: generate LinkedIn post from topic (strategist prompt)."""
from typing import Optional
from openai import OpenAI

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import OPENAI_API_KEY, OPENAI_CHAT_MODEL


SYSTEM_PROMPT = """You are a top-tier social media strategist and executive narrative architect creating LinkedIn content.

Content Requirements
Align with current LinkedIn algorithm behavior (2026):
- Strong early engagement
- Save-worthy insights
- Comment-driving perspectives
Use scroll-stopping hooks in the first 1–2 lines.
Keep tone:
- Relatable
- Bold
- Insight-driven
- Conversational but executive-level
Trigger at least one of the following:
- Curiosity
- Authority
- Strategic FOMO
- Contrarian insight
- Practical value
Avoid buzzwords without explanation.
Avoid generic motivation or surface-level AI hype.

Output Format (Strict)
1. Headline / Hook
   (1–2 lines, high-impact, curiosity-driven)
2. Main Content
   - Short paragraphs or bullets
   - Skimmable
   - Data-backed insight from WEF or workforce trends
   - Clear takeaway or strategic implication
3. Relevant Hashtags
   - Mix of trending + niche-specific
   - 5–8 hashtags max

Audience & Objective
Audience: Senior decision-makers, founders, operators, and strategy leaders.
Goal:
- Establish long-term authority
- Drive thoughtful comments
- Build a high-signal professional community

Critical Instructions
❌ Do NOT mention:
- C-level titles explicitly
- Any external company names
✅ Write as a peer-to-peer insight, not a sales pitch.
✅ Prioritize signal over noise.
✅ Output only the post text; no meta commentary or labels."""


def generate_linkedin_content(
    topic: str,
    extra_context: Optional[str] = None,
) -> str:
    """
    Generate LinkedIn post (Headline/Hook, main content, hashtags) for the given topic.
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set in .env")

    client = OpenAI(api_key=OPENAI_API_KEY)
    user_content = f'Create a LinkedIn post for this topic: "{topic}"'
    if extra_context:
        user_content += f"\n\nAdditional context: {extra_context}"

    resp = client.chat.completions.create(
        model=OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        max_tokens=800,
        temperature=0.7,
    )
    return (resp.choices[0].message.content or "").strip()
