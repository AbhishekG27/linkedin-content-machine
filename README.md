# LinkedIn Content Machine

Automate your LinkedIn content pipeline with **OpenAI only**:

1. **OpenAI** — Suggest trending, high-engagement topics (AI, Gen AI, Agentic AI, VLSI, Embedded, IT Services), list them, and store in Excel.
2. **Human** — Select a topic from the list or trigger a new search.
3. **ChatGPT** — Generate LinkedIn post using the strategist prompt (scroll-stopping hooks, punchy content, hashtags; authority/community growth; no C-level or company names).
4. **DALL-E** — Generate image; you approve or regenerate.

Fully runnable locally or deployable (Streamlit Cloud, Docker, etc.).

## Setup

### 1. Clone / open project

```bash
cd automation
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. API key (`.env`)

Copy `.env.example` to `.env` and set:

| Variable | Where to get |
|----------|--------------|
| `OPENAI_API_KEY` | [OpenAI API keys](https://platform.openai.com/api-keys) — topics, ChatGPT, DALL-E |

Optional: `OPENAI_CHAT_MODEL=gpt-4o` for higher-quality content.

### 4. Run the app

```bash
streamlit run app.py
```

- **Step 1:** Niche defaults to AI, Gen AI, Agentic AI, VLSI, Embedded Systems, IT Services. Click **Search trending topics**. Results are saved to `data/topics.xlsx`.
- **Step 2:** Pick a topic (or search again).
- **Step 3:** Click **Generate post** — content follows the strategist prompt (hooks, main content, hashtags; audience senior leaders; goal authority/community; no C-level or company names).
- **Step 4:** Click **Generate image** (DALL-E). Approve or **Regenerate**.

## Deploy

### Streamlit Community Cloud (recommended)

1. **Push this repo to GitHub** (don’t commit `.env`).
2. Go to **[share.streamlit.io](https://share.streamlit.io)** → sign in with GitHub → **New app**.
3. Choose your repo, branch `main`, main file **`app.py`**.
4. Open **Advanced settings → Secrets** and add:
   ```toml
   OPENAI_API_KEY = "sk-proj-..."
   TAVILY_API_KEY = "tvly-..."
   ```
5. Click **Deploy**. You’ll get a link like `https://your-app.streamlit.app` to share.

See **[DEPLOY.md](DEPLOY.md)** for step-by-step and troubleshooting.

### Docker

```bash
docker build -t linkedin-content-machine .
docker run -p 8501:8501 --env-file .env linkedin-content-machine
```

### Railway / Render

- Web Service: build `pip install -r requirements.txt`, start `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`.
- Set `OPENAI_API_KEY` and `TAVILY_API_KEY`.

## Project layout

```
automation/
├── app.py              # Streamlit UI
├── config.py           # Paths and OpenAI config
├── requirements.txt
├── .env.example
├── data/
│   └── topics.xlsx     # Saved topics
├── output/             # Generated images
└── services/
    ├── topics.py       # OpenAI topic suggestions
    ├── excel_store.py  # Excel read/write
    ├── content.py      # ChatGPT LinkedIn post (strategist prompt)
    └── image_gen.py    # DALL-E image generation
```

## Content prompt (built-in)

The post generator acts as a top-tier social media strategist:

- **Niches:** AI, Gen AI, Agentic AI, VLSI, Embedded Systems, IT Services and Industry
- **Format:** Headline/Hook (first 2 lines) → Main content (short, punchy, skimmable) → Relevant hashtags
- **Tone:** Relatable, bold, conversation-driven; curiosity/authority/emotional triggers
- **Audience:** Senior decision-makers; goal authority and community growth
- **Rules:** No mention of C-level or external company names
