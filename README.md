# AI Water Intake Tracker (Portfolio Project)

## Why I built it
- I wanted a hands-on way to combine Streamlit, FastAPI, SQLite, and LangChain/OpenAI into a single hydration dashboard that feels production-ready so I can talk confidently about full-stack Python work in interviews.
- This project helped me practice designing asynchronous APIs, managing lightweight persistence, and building data-rich UIs while keeping AI feedback loops and reminder logic easy to follow.

## What you can explore
1. **Streamlit dashboard (`dashboard.py`)** – goal management, weather-aware cues, smart reminders, streak/badge insights, mood & habit journals, CSV import/export, and AI reflections. Perfect place to demonstrate a polished UI and user flows.
2. **WaterIntakeAgent (`src/agent.py`)** – LangChain + OpenAI power instant intake analysis plus thoughtful weekly summaries; this is where LLM prompt engineering meets hydration logic.
3. **Persistence layer (`src/database.py`)** – encapsulates intake logs, goals, reminders, mood, habits, and leaderboard queries inside reusable helpers backed by `water_tracker.db`.
4. **API surface (`src/api.py`)** – FastAPI endpoints `/log_intake` and `/history/{user_id}` show how the project can scale beyond the Streamlit UI (and log telemetry via `src/logger.py`).
5. **Skills you can show** – async APIs, pandas data shaping, SQLite schema design, Streamlit layout, LangChain integration, dotenv/secret management, and lightweight logging.

## Architecture (quick visual)
```mermaid
flowchart LR
    UI[Streamlit dashboard]
    Agent[WaterIntakeAgent (LangChain + OpenAI)]
    DB[(SQLite: water_tracker.db)]
    API[FastAPI (`src/api.py`)]

    UI --> Agent
    UI --> DB
    UI --> API
    API --> Agent
    API --> DB
    Agent --> DB
```

## Running it locally
1. `cd` into the repo and create a venv (`python -m venv .venv` + `source .venv/bin/activate`).
2. `pip install -r requirements.txt`.
3. Copy `.env.example` if you keep one (or create `.env`) and populate `OPENAI_API_KEY` plus the optional `DATABASE_URL`.
4. `source .env` (or export the vars) before launching Streamlit.
5. Run `streamlit run dashboard.py`, play with logging intake, reminders, mood entries, and observe AI feedback & CSV export.
6. For the API runner: `uvicorn src.api:app --reload --host 0.0.0.0 --port 8000`, then `POST /log_intake` and `GET /history/{user_id}` to show API coverage.

## Learning notes (good conversation starters)
- **AI prompt engineering** – tuned contextual prompts to keep responses focused on hydration status and tips; great example of blending deterministic logic with LLMs during interviews.
- **Data modeling** – built helper functions for daily totals, streaks, and leaderboard queries so SQL stays centralized and reusable.
- **User experience** – added badges, streak metrics, reminders, and mood journals so the UI surfaces actionable insights, not just charts.
- **Error handling** – the dashboard gracefully handles missing user IDs, CSV validation, and API call failures, which shows attention to production resilience.

## What I might build next
1. Add background reminders (Celery/APS) and push notifications so the app reminds users even when the UI is closed.
2. Swap SQLite for Postgres + migrations to demonstrate readiness for multi-user deployments.
3. Add automated tests (API + persistence) and CI so the project includes confidence-building tooling.
4. Publish the Streamlit app or API somewhere (Render/Vercel) with a short walkthrough video for recruiters to click through.

## TL;DR for recruiters
- Full-stack Python hydration tracker using Streamlit UI + FastAPI + LangChain LLMs.
- SQLite-backed persistence with analytics (streaks, badges, leaderboard) and CSV import/export.
- Designed for demoing my ability to ship polished dashboards, AI assistants, and APIs in one repo.
