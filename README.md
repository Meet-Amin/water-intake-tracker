# AI Water Intake Tracker

## Overview
- Hydration monitoring app that blends a Streamlit dashboard, FastAPI API, and a LangChain/OpenAI assistant.
- Tracks intake, reminders, mood/habit notes, and exposes analytics with CSV import/export and shareable reflections.
- Keeps the architecture simple yet complete so you can run the UI or API locally, explore the LLM prompts, and see SQLite persistence in action.

## Architecture (diagram)
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

## Components
1. **Streamlit dashboard (`dashboard.py`)** – central UI for goal settings, reminders, weather-aware hydration cues, streak/badge insights, mood/habit journals, intake history visualizations, CSV import/export, shareable updates, and AI reflections.
2. **WaterIntakeAgent (`src/agent.py`)** – LangChain + OpenAI prompts synthesize intake feedback and weekly summaries, demonstrating prompt engineering with deterministic guardrails and safety-leaning responses.
3. **Persistence layer (`src/database.py`)** – unified helpers for intake logs, goals, reminders, mood entries, habits, and leaderboard analytics, backed by SQLite and initialized automatically.
4. **API surface (`src/api.py`)** – FastAPI exposes `/log_intake` and `/history/{user_id}`, enabling external clients to inject data while telemetry flows through `src/logger.py`.

## Technology stack
- Python 3.10+
- Streamlit (UI)
- FastAPI + Uvicorn (API host)
- LangChain + OpenAI (LLM agent)
- SQLite (`water_tracker.db`)
- pandas (data shaping)
- python-dotenv (config)

## Operational workflow
1. Create a virtual environment (`python -m venv .venv`) and activate it (`source .venv/bin/activate`).
2. Install dependencies: `pip install -r requirements.txt`.
3. Provide secrets via `.env` (or environment variables): `OPENAI_API_KEY` plus optional `DATABASE_URL`.
4. Source the environment (`source .env`) and launch Streamlit: `streamlit run dashboard.py`.
5. Configure a `user_id`, set goals, log intake/mood/habits, review AI feedback, and export CSV summaries.
6. Start the API for integrations: `uvicorn src.api:app --reload --host 0.0.0.0 --port 8000`, then POST to `/log_intake` or GET `/history/{user_id}` using tools like `curl` or Postman.

## Reliability & observability
- Tables auto-create on import; `water_tracker.db` sits in the repo root but can be redirected via `DATABASE_URL`.
- Reminders, mood, and habit logging include defensive checks (e.g., require a user ID, validate CSV schema) so the UI stays resilient.
- Logging via `src/logger.py` tracks API activity; you can expand it with structured sinks for production monitoring.
- AI usage is rate-limited by OpenAI; temperature sits at 0.5 to balance freshness and consistency, and you can swap models via `src/agent.py`.

## Future directions
1. Add scheduled reminders (Celery/APS) and push notifications for users outside the dashboard.
2. Introduce migrations/Postgres for multi-user deployments while preserving the existing SQLite helpers.
3. Build automated tests around the API and database helpers, then gate them in CI.
4. Deploy the stack (Streamlit + FastAPI) on a cloud host and capture a short demo for stakeholders.
