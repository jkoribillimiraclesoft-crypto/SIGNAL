# SIGNAL — AI Learning Intelligence (Streamlit)

## Run it

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key-here   # optional, only needed for "Generate today's briefing"
streamlit run streamlit_app.py
```

Then open the local URL it prints (usually http://localhost:8501).

## Notes

- All dashboard data (updates, trending tech, learning queue) is sample/demo data hardcoded in `streamlit_app.py`.
- The "Generate today's briefing" button calls the real Anthropic API using your `ANTHROPIC_API_KEY`. Without a key set, the dashboard still works — you'll just see an error message on that one button.
- To use a `secrets.toml` file instead of an environment variable, create `.streamlit/secrets.toml` with:
  ```toml
  ANTHROPIC_API_KEY = "your-key-here"
  ```
