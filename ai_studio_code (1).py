import streamlit as st
from sqlmodel import Session, select
import plotly.graph_objects as go
from database import engine, Article, create_db_and_tables
from intelligence import IntelligenceEngine
import os

# --- INITIALIZATION ---
create_db_and_tables()
st.set_page_config(page_title="AI DataPulse", page_icon="⚡", layout="wide")

# Load API Key
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY", "")
intel_engine = IntelligenceEngine(ANTHROPIC_API_KEY)

# Default Weights
if "weights" not in st.session_state:
    st.session_state.weights = {"gcp": 25, "de": 25, "ai": 20, "career": 15, "adoption": 10, "future": 5}

# --- STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0A0E13; color: #E7EDF4; }
    .card { background: #121821; border: 1px solid #232C38; border-radius: 12px; padding: 24px; margin-bottom: 16px; transition: 0.3s; }
    .card:hover { border-color: #4285F4; }
    .badge { padding: 4px 12px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-right: 8px; }
    .must { background: #45D6C6; color: #06231F; }
    .important { background: #E8A23D; color: #06231F; }
    .explore { background: #D9C558; color: #06231F; }
    .watch { background: #5B6774; color: #E7EDF4; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚡ AI DataPulse")
    st.caption("Intelligence for GCP Data Engineers")
    menu = st.radio("Navigation", ["Current Week", "Learning Roadmap", "Trend Analytics", "Settings"])
    st.divider()
    
    if st.button("🔄 Sync Latest Intelligence"):
        st.toast("Connecting to Intelligence Pipeline...")
        # In a real app, this calls the scrapers + LLM analysis
        # For this version, we will seed with data if empty
        with Session(engine) as session:
            if not session.exec(select(Article)).first():
                from seed_data import seed_production_data
                seed_production_data(session, st.session_state.weights, intel_engine)
                st.rerun()

# --- CONTENT LOGIC ---

def render_article(art: Article):
    st.markdown(f"""
    <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div>
                <span class="badge {art.priority}">{art.priority}</span>
                <span style="color: #5B6774; font-size: 13px;">{art.source} • {art.category}</span>
            </div>
            <div style="color: #4285F4; font-weight: 700; font-size: 20px;">{int(art.relevance_score)}</div>
        </div>
        <h3 style="margin: 0 0 12px 0;">{art.title}</h3>
        <p style="color: #8B97A6; line-height: 1.6;">{art.summary}</p>
        <div style="background: #0D1218; padding: 12px; border-radius: 8px; border-left: 3px solid #34A853;">
            <strong style="color: #34A853; font-size: 12px;">GCP USE CASE:</strong><br>
            <span style="font-size: 14px;">{art.gcp_use_case}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("Deep Dive: Career Impact & Learning"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**What's New?**\n\n{art.whats_new}")
            st.markdown(f"**Why Learn This?**\n\n{art.why_learn}")
        with col2:
            st.markdown(f"**Technical Relevance Breakdown**")
            # Mini bar chart for scores
            for k, v in art.scores_json.items():
                st.caption(f"{k.upper()}: {v}")
                st.progress(v/100)

if menu == "Current Week":
    st.subheader("🔥 This Week's Intelligence")
    with Session(engine) as session:
        articles = session.exec(select(Article).order_by(Article.relevance_score.desc())).all()
    
    if not articles:
        st.info("No data available. Click 'Sync Latest Intelligence' in the sidebar.")
    else:
        for art in articles:
            render_article(art)

elif menu == "Learning Roadmap":
    st.subheader("🎓 My AI Learning Roadmap")
    with Session(engine) as session:
        must_learn = session.exec(select(Article).where(Article.priority == "must")).all()
        next_learn = session.exec(select(Article).where(Article.priority == "important")).all()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔴 Learn Now")
        for a in must_learn:
            st.markdown(f"- **{a.title}**\n*{a.why_learn}*")
    with col2:
        st.markdown("### 🟠 Learn Next")
        for a in next_learn:
            st.markdown(f"- **{a.title}**")

elif menu == "Trend Analytics":
    st.subheader("📊 Ecosystem Trends")
    with Session(engine) as session:
        all_art = session.exec(select(Article)).all()
    
    trends = intel_engine.analyze_trend(all_art)
    if trends:
        fig = go.Figure(data=[go.Pie(labels=list(trends.keys()), values=list(trends.values()), hole=.3)])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#E7EDF4")
        st.plotly_chart(fig)
    else:
        st.info("Sync data to see trends.")

elif menu == "Settings":
    st.subheader("⚙️ Intelligence Configuration")
    st.write("Personalize your ranking algorithm.")
    for k, v in st.session_state.weights.items():
        st.session_state.weights[k] = st.slider(f"{k.upper()} Weight", 0, 100, v)
    if st.button("Save & Re-rank Historical Data"):
        # In production, this would trigger a background task to recalculate scores
        st.success("Weights updated for future syncs.")