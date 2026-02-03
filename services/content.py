"""OpenAI ChatGPT: generate LinkedIn post from topic (strategist prompt)."""
from typing import Optional
from openai import OpenAI

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import OPENAI_API_KEY, OPENAI_CHAT_MODEL


SYSTEM_PROMPT = """Act as a top-tier social media strategist and trend analyst.
Create high-engagement, viral-ready content for LinkedIn in AI, Gen AI, Agentic AI, VLSI, Embedded Systems, IT Services and Industry.

Requirements:
• Content must align with current trends, audience behavior, and platform algorithms
• Use scroll-stopping hooks in the first 2 lines
• Keep the tone relatable, bold, and conversation-driven
• Incorporate curiosity, authority, or emotional triggers (FOMO, insights, controversy, or value)
• Optimize for maximum reach, saves, and comments

Output format:
1. Headline / Hook (first 2 lines — scroll-stopping)
2. Main content (short, punchy, skimmable)
3. Relevant hashtags (trending + niche-specific)

Audience: Senior decision-makers and industry leaders.
Goal: Authority building and community growth.

Instructions: Do not mention "C-level" or external company names in the post. Output only the post text, no meta commentary."""


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
