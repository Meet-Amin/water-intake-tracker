# AI Water Intake Tracker

## Overview
- AI-powered hydration management platform combining a Streamlit dashboard, AI assistant, and FastAPI endpoints to help individuals track intake, maintain habits, and share progress with accountability signals.
- Built for industrial-grade deployment, the project emphasizes automated insights, lightweight data persistence, and secure key management so teams can onboard new users without reinventing the data pipeline.

## Architecture
- **Streamlit dashboard (`dashboard.py`)** – orchestrates the entire user experience: goal setting, reminders, weather-aware advice, streak analysis, badges, intake history charts, mood/habit journaling, AI coaching feedback, CSV import/export, and data sharing options.
- **WaterIntakeAgent (`src/agent.py`)** – wraps LangChain + OpenAI to generate motivating feedback and weekly reflections based on the latest hydration totals.
- **SQLite persistence layer (`src/database.py`)** – centralized access layer with helpers for intake logs, goals, reminders, mood journal, habits, and leaderboard analytics; tables auto-create on import.
- **FastAPI service (`src/api.py`)** – exposes secure endpoints for remote intake submissions and retrieval, mirroring the dashboard workflow while logging telemetry via `src/logger.py`.

## Key Features
1. Personalized daily goals with persistence, reminders, and CSV imports for historical data.
2. Automated streak, badge, and leaderboard calculations with visual progress indicators.
3. AI feedback loops (instant intake analysis and weekly reflection summaries) powered by GPT-3.5.
4. Weather-aware hydration cues plus mood/habit journaling to correlate well-being with intake trends.
5. Lightweight API surface (`/log_intake`, `/history/{user_id}`) for external integrations or mobile companions.

## Technology Stack
- Python 3.10+
- Streamlit (UI)
- FastAPI + Uvicorn (API)
- LangChain + OpenAI (LLM agent)
- SQLite (`water_tracker.db`)
- Pandas (data shaping)
- python-dotenv (config)

## Getting Started

### Prerequisites
1. Clone the repository and change into the project root.
2. Create and activate a virtual environment (recommended: `python -m venv .venv` + `source .venv/bin/activate`).
3. Install dependencies with `pip install -r requirements.txt`.

### Environment configuration
1. Copy `.env` (which should remain untracked) and populate:
   - `OPENAI_API_KEY` – valid key with access to `gpt-3.5-turbo` or newer.
   - `DATABASE_URL` – optional override; defaults to `water_tracker.db` in the repo root.
2. Never commit real keys. Rotate them regularly and inject secrets via CI/runtime secrets management in production.

### Database
- All necessary tables are created automatically when `src/database.py` is imported.
- The default SQLite file (`water_tracker.db`) lives in the project root, but you can point `DATABASE_URL` at another file path or mount a shared volume in production.
- Use `sqlite3 water_tracker.db` locally for manual inspection, backups, or migrations.

### Running the dashboard
1. Export your `.env` values: `source .env`.
2. Launch Streamlit: `streamlit run dashboard.py`.
3. Log in (any `user_id` works), set goals, add intake/reminders, and experiment with CSV import/export.

### Running the API
1. Start the FastAPI worker: `uvicorn src.api:app --reload --host 0.0.0.0 --port 8000`.
2. POST intake logs:
   ```json
   POST /log_intake
   {
     "user_id": "user_123",
     "intake_ml": 350
   }
   ```
3. GET history: `GET /history/user_123`.
4. Monitor logs via the standard `logging` module; `src/logger.py` centralizes this behavior.

## Operational Notes
- **AI Usage** – Each dashboard intake or API POST invokes OpenAI. Be mindful of token usage and temperature (set to 0.5). Switch to a GPT-4-style model by adjusting `model=` in `src/agent.py` if budget allows.
- **Weather data** – The dashboard calculates tips using manual temperature/humidity inputs stored in `st.session_state`.
- **CSV import** – Accepts `intake_ml`, `date` (YYYY-MM-DD), and optional `user_id`. Invalid rows are skipped silently; monitor the UI alert for feedback.
- **Logging & metrics** – Intake data is aggregated in `daily_totals`; streaks, badges, and leaderboard calculations rely on these summaries.

## Testing & Validation
- No automated tests are bundled yet. Apply `pytest` or similar locally once added.
- Manual checks: log intake, verify AI feedback, insert mock mood/habit entries, and confirm leaderboard snapshots.

## Contribution & Workflow
1. Follow the existing style (PEP 8, snake_case for functions, small helper utilities in `src/`).
2. Add docs/tests when extending features (e.g., new reminder types or LLM prompts).
3. Submit PRs with clear descriptions, checklist of manual validation steps, and note any required secret/credential updates.

## Troubleshooting
- `ModuleNotFoundError: No module named 'langchain_openai'` → reinstall with `pip install -r requirements.txt`.
- `OpenAI key invalid` → regenerate in the OpenAI dashboard and update `.env`; restart Streamlit/UVicorn so the new key loads.
- `SQLite locked` → ensure no other process (or parallel Streamlit session) is writing to `water_tracker.db`. Delete `.db-journal` if stale.

## Future roadmap
- Add scheduled reminders via background scheduler (Celery/APS) for push notifications.
- Introduce unit + integration tests (API, database layer) with GitHub Actions.
- Replace SQLite with Postgres for multi-user deployments and add migrations.
