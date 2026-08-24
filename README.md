# VANTAGE — GCP Data Engineering AI Intelligence

A personalized AI intelligence dashboard for a GCP Data Engineer, built on the same
prototype pattern as the earlier SIGNAL dashboard, extended with:

- A default profile (GCP Data Engineer) with a configurable, weighted Personal
  Relevance Score (GCP 25% / Data Engineering 25% / AI 20% / Career 15% /
  Adoption 10% / Future 5% by default — adjustable on the Profile page, and
  every ranking in the app recomputes live when you change the weights).
- Tiered source categories (Tier 1 GCP-critical → Tier 4 background AI news).
- "Can I use this in a GCP data engineering project?" Yes / Potentially / No
  on every update, with a concrete use case.
- A Learning Roadmap (Learn Now / Learn Next / Explore Later / Watch) derived
  from the live scores, not hardcoded.
- A Project Ideas page with three concrete GCP + AI project concepts.
- A "Generate my weekly report" button that calls the real Anthropic API to
  produce a personalized weekly report (most important updates, what changed
  in GCP, what changed in AI, what to learn, what to build, career impact).

## Run it

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key-here   # only needed for "Generate my weekly report"
streamlit run streamlit_app.py
```

Then open the local URL it prints (usually http://localhost:8501).

## Notes

- All update data (titles, sources, scores) is sample/demo data hardcoded in
  `streamlit_app.py`, clearly not a live feed.
- Without an `ANTHROPIC_API_KEY` set, everything works except the weekly
  report button, which will show a clear error instead of failing silently.
- To use `secrets.toml` instead of an environment variable, create
  `.streamlit/secrets.toml` with:
  ```toml
  ANTHROPIC_API_KEY = "your-key-here"
  ```

## What's next (not built yet)

The full spec calls for a production pipeline: LangGraph agents doing
research → relevance scoring → summarization → career impact → learning
recommendation, backed by SQLite + ChromaDB, pulling from real RSS/API
sources. This prototype hardcodes that pipeline's *output* so the UI and
scoring model can be validated first. The next step is wiring a real
ingestion + agent pipeline behind this same UI.
