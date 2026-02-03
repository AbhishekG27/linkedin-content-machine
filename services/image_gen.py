"""Image generation: DALL-E from topic."""
import time
from pathlib import Path
from typing import Optional, Tuple

import requests
from openai import OpenAI

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import (
    OPENAI_API_KEY,
    DALLE_MODEL,
    DALLE_SIZE,
    DALLE_QUALITY,
    OUTPUT_DIR,
    ensure_dirs,
)


def generate_post_image(
    topic: str,
    style: str = "professional, clean, LinkedIn-style graphic",
) -> Tuple[Optional[Path], Optional[str]]:
    """
    Generate an image for the LinkedIn post using DALL-E 3.
    Returns (local_file_path, None) on success, or (None, error_message).
    """
    if not OPENAI_API_KEY:
        return None, "OPENAI_API_KEY is not set in .env"

    ensure_dirs()
    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = (
        f"Create a single, professional image suitable for a LinkedIn post. "
        f"Topic/theme: {topic}. Style: {style}. "
        f"No text overlay in the image. High quality, suitable for business audience."
    )

    try:
        resp = client.images.generate(
            model=DALLE_MODEL,
            prompt=prompt,
            size=DALLE_SIZE,
            quality=DALLE_QUALITY,
            n=1,
        )
        url = resp.data[0].url
        if not url:
            return None, "No image URL in response"
        img_resp = requests.get(url, timeout=30)
        img_resp.raise_for_status()
        safe_name = "".join(
            c if c.isalnum() or c in " -_" else "_" for c in topic[:50]
        )
        fpath = OUTPUT_DIR / f"linkedin_image_{safe_name}_{int(time.time())}.png"
        fpath.write_bytes(img_resp.content)
        return fpath, None
    except Exception as e:
        return None, str(e)
