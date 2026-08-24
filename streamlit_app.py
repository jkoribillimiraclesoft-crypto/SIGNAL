import os
import json
import streamlit as st
import plotly.graph_objects as go

# ============================================================== CONFIG

st.set_page_config(page_title="VANTAGE — GCP Data Engineering AI Intelligence", page_icon="☁️", layout="wide")

PRIORITY = {
    "must": {"label": "Must Learn", "emoji": "🔴", "color": "#45D6C6"},
    "important": {"label": "Important", "emoji": "🟠", "color": "#E8A23D"},
    "explore": {"label": "Worth Exploring", "emoji": "🟡", "color": "#D9C558"},
    "watch": {"label": "Watch", "emoji": "⚪", "color": "#5B6774"},
}
GCP_BLUE = "#4285F4"
GCP_GREEN = "#34A853"

DEFAULT_WEIGHTS = {"gcp": 25, "de": 25, "ai": 20, "career": 15, "adoption": 10, "future": 5}
WEIGHT_LABELS = {"gcp": "GCP Relevance", "de": "Data Engineering Relevance", "ai": "AI Relevance",
                  "career": "Career Impact", "adoption": "Industry Adoption", "future": "Future Potential"}

DEFAULT_PROFILE = dict(
    role="GCP Data Engineer",
    expertise="Data Engineering, Google Cloud Platform, Data pipelines, Data processing, Data platforms",
    ai_experience="Has experience working with AI models; interested in applying AI to data engineering",
)

# ============================================================== SAMPLE DATA
# Each item carries raw component scores (0-100). The weighted Personal
# Relevance Score is computed live from session_state.weights, so adjusting
# the profile weights on the Profile page re-ranks everything in the app.

UPDATES = [
    dict(id=1, title="Vertex AI adds native BigQuery ML integration for agent-based feature engineering",
         source="Google Cloud Blog", date="Aug 24, 2026", tier=1, category="Vertex AI + BigQuery",
         is_gcp=True, is_de=True,
         summary="Vertex AI pipelines can now read and write BigQuery ML models directly, letting agents trigger feature engineering and model retraining as part of a data pipeline run.",
         whats_new="A first-party connector lets Vertex AI Pipelines call BigQuery ML training and inference jobs as pipeline steps, with lineage tracked automatically.",
         why_matters="Removes a major integration gap between BigQuery-based data platforms and Vertex AI's agent and pipeline tooling.",
         why_learn="As a GCP Data Engineer, this lets you build pipelines where feature engineering, model retraining, and serving all live inside the tooling you already use — BigQuery and Vertex AI — instead of stitching together custom glue code.",
         what_to_learn=["Vertex AI Pipelines", "BigQuery ML", "Feature engineering automation"],
         gcp_use="Yes", gcp_use_case="Automate retraining of a BigQuery ML churn model directly from a Vertex AI Pipeline triggered by new data landing in BigQuery.",
         scores=dict(gcp=95, de=92, ai=88, career=90, adoption=80, future=75)),

    dict(id=2, title="BigQuery vector search reaches general availability",
         source="Google Cloud Release Notes", date="Aug 23, 2026", tier=1, category="BigQuery",
         is_gcp=True, is_de=True,
         summary="BigQuery now supports native vector search over embedding columns at GA, removing the need for a separate vector database for many RAG use cases built on GCP data.",
         whats_new="VECTOR_SEARCH and CREATE VECTOR INDEX are now GA in BigQuery, with support for approximate nearest-neighbor search over billions of rows.",
         why_matters="Many RAG architectures previously required exporting data to a dedicated vector store; this keeps embeddings and search inside the existing warehouse.",
         why_learn="You can now build RAG applications directly on top of data already living in BigQuery, without standing up and syncing a separate vector database — a meaningful simplification for GCP-based data platforms.",
         what_to_learn=["BigQuery vector search", "RAG architecture", "Embeddings in SQL workflows"],
         gcp_use="Yes", gcp_use_case="Build a support-ticket RAG assistant that embeds ticket text with a BigQuery ML embedding model and searches it with VECTOR_SEARCH, with no external vector DB.",
         scores=dict(gcp=96, de=94, ai=85, career=88, adoption=85, future=70)),

    dict(id=3, title="Anthropic ships native multi-agent orchestration API",
         source="Anthropic Blog", date="Aug 24, 2026", tier=2, category="AI Agents",
         is_gcp=False, is_de=False,
         summary="A new API primitive lets developers spawn, coordinate, and hand off work between sub-agents without hand-rolled orchestration logic.",
         whats_new="Native support for spawning child agents with scoped tool access and automatic result aggregation back to a parent agent.",
         why_matters="Multi-agent patterns have been mostly bespoke until now; a first-party primitive lowers the bar for production agent systems.",
         why_learn="Useful general agent-building knowledge, but it's platform-agnostic — it doesn't yet integrate directly with GCP data tooling, so it's worth exploring rather than an immediate priority for your pipeline work.",
         what_to_learn=["AI Agents", "Tool use / function calling", "Agent orchestration patterns"],
         gcp_use="Potentially", gcp_use_case="Could be used to build a multi-agent troubleshooting assistant for GCP pipelines, but would need custom GCP tool integrations first.",
         scores=dict(gcp=40, de=55, ai=94, career=80, adoption=70, future=85)),

    dict(id=4, title="MCP gains a standardized 'skills' extension across major clients",
         source="MCP Working Group", date="Aug 23, 2026", tier=2, category="MCP",
         is_gcp=False, is_de=False,
         summary="A cross-vendor extension to the Model Context Protocol lets servers expose reusable, versioned 'skills' rather than raw tools, now supported by three major clients.",
         whats_new="A formal spec for packaging instructions + tools + resources as a single discoverable unit.",
         why_matters="Standardization reduces fragmentation between MCP clients and makes skill-based extensions portable across products.",
         why_learn="MCP is becoming the common interface between models and external systems, including data tools. Worth tracking now so you're ready when GCP-native MCP servers for BigQuery or Dataflow mature.",
         what_to_learn=["Model Context Protocol", "MCP servers", "Skill packaging"],
         gcp_use="Potentially", gcp_use_case="An MCP server exposing BigQuery as a skill could let an agent safely query your warehouse — not yet a standard GCP offering.",
         scores=dict(gcp=45, de=60, ai=90, career=75, adoption=65, future=85)),

    dict(id=5, title="dbt adds native AI-generated data quality tests",
         source="dbt Labs", date="Aug 22, 2026", tier=1, category="Data Quality + AI",
         is_gcp=False, is_de=True,
         summary="dbt can now generate suggested data quality tests from column profiling and historical anomaly patterns, reducing manual test-writing for new models.",
         whats_new="An LLM-backed test generator proposes not-null, range, and freshness tests based on observed data patterns, which engineers can accept or edit.",
         why_matters="Data quality testing is one of the most time-consuming parts of maintaining a data platform; automating first-draft tests meaningfully cuts that burden.",
         why_learn="This is squarely in your day-to-day work. If you run dbt on BigQuery, this can directly reduce the time you spend hand-writing tests for new pipelines.",
         what_to_learn=["dbt AI test generation", "Data quality automation", "Anomaly-based test design"],
         gcp_use="Yes", gcp_use_case="Run dbt's AI test generator against a new BigQuery model to get a first draft of quality tests before a pipeline goes to production.",
         scores=dict(gcp=60, de=95, ai=80, career=85, adoption=75, future=65)),

    dict(id=6, title="Airflow community releases LLM-powered DAG failure explainer",
         source="GitHub Trending", date="Aug 21, 2026", tier=1, category="Data Pipelines + AI",
         is_gcp=False, is_de=True,
         summary="A community Airflow plugin uses an LLM to read task logs on failure and produce a plain-language explanation plus suggested fix, surfaced directly in the Airflow UI.",
         whats_new="A new provider package hooks into Airflow's on-failure callback to summarize stack traces and logs into a short diagnosis.",
         why_matters="Cuts the time spent digging through logs during pipeline incidents, especially for less experienced on-call engineers.",
         why_learn="Directly applicable if you run Airflow (including Cloud Composer) — this is the kind of AI-assisted troubleshooting tool worth piloting on your own DAGs.",
         what_to_learn=["Airflow provider packages", "LLM log analysis", "Pipeline observability"],
         gcp_use="Yes", gcp_use_case="Install the plugin on a Cloud Composer environment so failed DAG runs get an automatic plain-language diagnosis before you open the logs.",
         scores=dict(gcp=50, de=90, ai=82, career=80, adoption=60, future=60)),

    dict(id=7, title="arXiv paper proposes a cheaper RAG evaluation harness",
         source="arXiv", date="Aug 22, 2026", tier=2, category="RAG",
         is_gcp=False, is_de=False,
         summary="Researchers introduce a sampling-based evaluation method that approximates full retrieval-quality benchmarks at roughly a tenth of the compute cost.",
         whats_new="A stratified-sampling technique for scoring retrieval and generation quality without running the full benchmark suite.",
         why_matters="Cheap, frequent RAG evaluation makes it practical to catch retrieval regressions in CI rather than only in periodic audits.",
         why_learn="Relevant background if you build RAG on top of BigQuery vector search, but it's a research technique rather than something to apply immediately.",
         what_to_learn=["RAG", "LLM evaluation", "Retrieval quality metrics"],
         gcp_use="Potentially", gcp_use_case="Could inform how you evaluate a BigQuery-vector-search-based RAG pipeline before shipping it.",
         scores=dict(gcp=30, de=40, ai=85, career=55, adoption=50, future=70)),

    dict(id=8, title="Open-weight 30B model matches proprietary models on coding benchmarks",
         source="GitHub Release Notes", date="Aug 22, 2026", tier=3, category="Open-Source LLMs",
         is_gcp=False, is_de=False,
         summary="A newly released open-weight model reaches parity with closed frontier models on two widely used coding benchmarks while running on a single high-end consumer GPU.",
         whats_new="Open weights, training recipe, and eval harness released together.",
         why_matters="Narrows the gap between open and closed models, expanding self-hosted deployment options.",
         why_learn="Worth knowing about if data residency or cost ever pushes you toward self-hosting models on GCE or GKE, but not an immediate priority for pipeline work.",
         what_to_learn=["Open-weight models", "Self-hosted inference"],
         gcp_use="Potentially", gcp_use_case="Could be self-hosted on GKE for teams with strict data residency requirements instead of calling an external API.",
         scores=dict(gcp=20, de=35, ai=80, career=50, adoption=70, future=60)),

    dict(id=9, title="LangGraph reaches 1.0 with durable execution",
         source="LangChain Blog", date="Aug 20, 2026", tier=3, category="AI Orchestration",
         is_gcp=False, is_de=False,
         summary="LangGraph's 1.0 release adds durable, checkpointed execution for long-running agent graphs, making it more viable for production workflows that span minutes or hours.",
         whats_new="Built-in checkpointing means an agent graph can resume from a failure point instead of restarting from scratch.",
         why_matters="Long-running, stateful agent workflows have historically been fragile; durable execution addresses a real production gap.",
         why_learn="Worth exploring if you plan to build agent-orchestrated data workflows — durable execution matters a lot once agents are coordinating multi-step pipeline work.",
         what_to_learn=["LangGraph", "Durable agent execution", "Agent state management"],
         gcp_use="Potentially", gcp_use_case="Could orchestrate a multi-step GCP data-quality agent (profile → detect → fix → verify) with resilience to mid-run failures.",
         scores=dict(gcp=35, de=55, ai=78, career=70, adoption=65, future=75)),

    dict(id=10, title="Snowflake announces native LLM function for SQL generation",
         source="Snowflake Blog", date="Aug 19, 2026", tier=2, category="AI-Powered Analytics",
         is_gcp=False, is_de=True,
         summary="Snowflake adds a built-in function that translates natural-language questions into SQL against a given schema, competing directly with similar GCP capabilities.",
         whats_new="A SQL function wraps an LLM call scoped to the query's table schema, returning generated SQL for review before execution.",
         why_matters="Signals natural-language-to-SQL is becoming a standard warehouse feature rather than a bolt-on tool, which raises the bar for BigQuery to match.",
         why_learn="Worth knowing about as competitive context — it's a strong signal for where BigQuery's own natural-language features are likely headed, even though this specific feature isn't GCP-native.",
         what_to_learn=["Natural language to SQL", "Warehouse-native AI features"],
         gcp_use="No", gcp_use_case="Not directly usable on GCP, but useful to understand as the pattern BigQuery's equivalent features are likely to follow.",
         scores=dict(gcp=25, de=85, ai=75, career=70, adoption=70, future=55)),

    dict(id=11, title="Hacker News debates whether agent frameworks are over-engineered",
         source="Hacker News", date="Aug 20, 2026", tier=4, category="AI Agents",
         is_gcp=False, is_de=False,
         summary="A widely discussed thread argues many agent frameworks add abstraction without solving core reliability problems.",
         whats_new="No product news — a community discussion surfacing recurring critiques of agent framework complexity.",
         why_matters="Useful signal on where practitioners are hitting friction with current agent tooling.",
         why_learn="Background context only — not something to act on for your pipeline work.",
         what_to_learn=["Agent framework trade-offs"],
         gcp_use="No", gcp_use_case="Not applicable — this is a discussion thread, not a tool or capability.",
         scores=dict(gcp=10, de=20, ai=60, career=30, adoption=40, future=40)),

    dict(id=12, title="Meta releases multimodal benchmark suite for video understanding",
         source="Meta AI Blog", date="Aug 18, 2026", tier=4, category="Consumer / Research AI",
         is_gcp=False, is_de=False,
         summary="A new benchmark suite targets long-form video understanding, an area where current multimodal models still lag behind image and text performance.",
         whats_new="Standardized tasks for temporal reasoning and long-context video question answering.",
         why_matters="Gives the field a shared way to measure progress on a historically underbenchmarked capability.",
         why_learn="Not relevant to data engineering work — safe to skip unless multimodal applications are on your roadmap.",
         what_to_learn=["Multimodal models (background only)"],
         gcp_use="No", gcp_use_case="No practical data engineering use case.",
         scores=dict(gcp=5, de=10, ai=65, career=20, adoption=45, future=50)),
]

PROJECT_IDEAS = [
    dict(name="AI Data Quality Agent", icon="🩺",
         description="A GCP-based agent that continuously watches your BigQuery tables and flags problems before they hit downstream dashboards.",
         bullets=["Profiles new data and detects anomalies against historical patterns",
                  "Generates SQL data-quality checks automatically (nulls, ranges, freshness)",
                  "Explains failures in plain language, not just a stack trace",
                  "Suggests concrete fixes or a corrected dbt test"]),
    dict(name="AI Pipeline Assistant", icon="🛠️",
         description="An assistant that reads Airflow/Cloud Composer logs so you don't have to dig through them during an incident.",
         bullets=["Reads pipeline logs on failure",
                  "Identifies the likely root cause across retries",
                  "Explains the error in plain language",
                  "Generates a troubleshooting checklist and a suggested fix"]),
    dict(name="Natural Language → BigQuery", icon="💬",
         description="Let stakeholders ask business questions in plain English and get back a reviewed BigQuery query and result.",
         bullets=["Accepts a question like 'customers whose revenue dropped over 20%'",
                  "Generates BigQuery SQL scoped to your actual schema",
                  "Shows the SQL for review before executing",
                  "Returns results plus a plain-language summary"]),
]

# ============================================================== STYLE

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
.stApp { background-color: #0A0E13; color: #E7EDF4; }
section[data-testid="stSidebar"] { background-color: #0D1218; border-right: 1px solid #232C38; }
h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif !important; }
.mono { font-family: 'IBM Plex Mono', monospace; }
.card { background: #121821; border: 1px solid #232C38; border-radius: 12px; padding: 18px; margin-bottom: 14px; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: 600;
  font-family: 'IBM Plex Mono', monospace; letter-spacing: 0.3px; margin-right: 6px; }
.tag { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 12px; border: 1px solid #232C38;
  color: #E7EDF4; margin: 2px 4px 2px 0; }
.muted { color: #8B97A6; }
.faint { color: #5B6774; font-size: 12px; font-family: 'IBM Plex Mono', monospace; }
.stat-box { background: #121821; border: 1px solid #232C38; border-radius: 10px; padding: 14px 16px; }
.stat-label { font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: #5B6774; letter-spacing: 0.5px; text-transform: uppercase; }
.stat-value { font-family: 'Space Grotesk', sans-serif; font-size: 26px; font-weight: 700; margin-top: 4px; }
.rank { font-family: 'Space Grotesk', sans-serif; font-size: 22px; font-weight: 700; color: #4285F4; width: 34px; display: inline-block; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ============================================================== STATE

if "weights" not in st.session_state:
    st.session_state.weights = dict(DEFAULT_WEIGHTS)
if "profile" not in st.session_state:
    st.session_state.profile = dict(DEFAULT_PROFILE)
if "report" not in st.session_state:
    st.session_state.report = None
if "report_error" not in st.session_state:
    st.session_state.report_error = None


def weighted_score(item):
    w = st.session_state.weights
    total_w = sum(w.values()) or 1
    s = item["scores"]
    raw = sum(s[k] * w[k] for k in w)
    return round(raw / total_w * 100 / 100, 1) if total_w != 100 else round(raw / 100, 1)


def priority_for(score):
    if score >= 85:
        return "must"
    elif score >= 70:
        return "important"
    elif score >= 50:
        return "explore"
    return "watch"


def badge(priority_key):
    p = PRIORITY[priority_key]
    return f'<span class="badge" style="background:{p["color"]}; color:#06231F;">{p["emoji"]} {p["label"]}</span>'


def gcp_use_badge(val):
    color = {"Yes": GCP_GREEN, "Potentially": "#E8A23D", "No": "#5B6774"}[val]
    return f'<span class="badge" style="background:{color}; color:#06231F;">{val}</span>'


SCORED = [(u, weighted_score(u)) for u in UPDATES]
SCORED.sort(key=lambda t: -t[1])

# ============================================================== SIDEBAR

with st.sidebar:
    st.markdown("### ☁️ VANTAGE")
    st.caption("GCP Data Engineering AI Intelligence")
    page = st.radio("Navigate", ["🏠 Overview", "🔥 Top For You", "☁️ GCP + AI", "📰 AI Updates",
                                  "🎓 Learning Roadmap", "💡 Project Ideas", "📊 Weekly Report", "⚙️ Profile"],
                     label_visibility="collapsed")
    st.divider()
    st.caption(f"Profile: **{st.session_state.profile['role']}**")
    st.caption("Sample data for prototype purposes — connect live sources to go live.")

page = page.split(" ", 1)[1] if " " in page else page

# ============================================================== HELPERS FOR CARDS

def render_score_breakdown(item):
    w = st.session_state.weights
    cols = st.columns(6)
    for col, key in zip(cols, w.keys()):
        with col:
            st.markdown(f'<div class="faint">{WEIGHT_LABELS[key]}</div>'
                        f'<div style="font-family:\'IBM Plex Mono\',monospace; font-size:15px; font-weight:600;">{item["scores"][key]}</div>',
                        unsafe_allow_html=True)


def render_update_card(item, score, rank=None):
    pr = priority_for(score)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    top_l, top_r = st.columns([5, 1])
    with top_l:
        rank_html = f'<span class="rank">#{rank}</span> ' if rank else ""
        st.markdown(f'{rank_html}{badge(pr)}<span class="faint">Tier {item["tier"]} · {item["category"]}</span>', unsafe_allow_html=True)
        st.markdown(f'#### {item["title"]}')
        st.markdown(f'<span class="muted">{item["summary"]}</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="faint">{item["source"]} · {item["date"]}</span>', unsafe_allow_html=True)
    with top_r:
        st.metric("Personal Relevance", f'{score:.0f}/100')

    with st.expander("Why should I learn this? (full breakdown)"):
        st.markdown(f"**What's New?**  \n{item['whats_new']}")
        st.markdown(f"**Why Does It Matter?**  \n{item['why_matters']}")
        st.markdown(f"**Why Should I Learn This?**  \n{item['why_learn']}")
        st.markdown("**What Should I Learn?**")
        st.markdown("".join(f'<span class="tag">{t}</span>' for t in item["what_to_learn"]), unsafe_allow_html=True)
        st.markdown(f"**Can I use this in a GCP data engineering project?** {gcp_use_badge(item['gcp_use'])}", unsafe_allow_html=True)
        st.markdown(f"<span class='muted'>{item['gcp_use_case']}</span>", unsafe_allow_html=True)
        st.markdown("**Score breakdown**")
        render_score_breakdown(item)
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================== OVERVIEW

if page == "Overview":
    st.markdown("## Overview")
    c1, c2, c3, c4, c5 = st.columns(5)
    must_count = sum(1 for u, s in SCORED if priority_for(s) == "must")
    avg_score = sum(s for _, s in SCORED) / len(SCORED)
    for col, label, value, color in [
        (c1, "AI Updates Today", len(UPDATES), "#E7EDF4"),
        (c2, "GCP Updates", sum(1 for u in UPDATES if u["is_gcp"]), GCP_BLUE),
        (c3, "Data Engineering Updates", sum(1 for u in UPDATES if u["is_de"]), "#E7EDF4"),
        (c4, "Must Learn Topics", must_count, PRIORITY["must"]["color"]),
        (c5, "Avg Personal Relevance", f"{avg_score:.0f}", GCP_GREEN),
    ]:
        with col:
            st.markdown(f'<div class="stat-box"><div class="stat-label">{label}</div>'
                        f'<div class="stat-value" style="color:{color};">{value}</div></div>', unsafe_allow_html=True)

    st.markdown("")
    col1, col2 = st.columns([1.3, 1])
    with col1:
        st.markdown("**Personal Relevance Score by Update**")
        titles = [u["title"][:38] + ("…" if len(u["title"]) > 38 else "") for u, s in SCORED]
        scores = [s for u, s in SCORED]
        colors = [PRIORITY[priority_for(s)]["color"] for s in scores]
        fig = go.Figure(go.Bar(x=scores, y=titles, orientation="h", marker_color=colors))
        fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)",
                           plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#8B97A6", size=11),
                           xaxis=dict(gridcolor="#232C38", range=[0, 100]), yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("**Learning Priority Distribution**")
        counts = {}
        for u, s in SCORED:
            pr = priority_for(s)
            counts[PRIORITY[pr]["label"]] = counts.get(PRIORITY[pr]["label"], 0) + 1
        fig = go.Figure(go.Pie(labels=list(counts.keys()), values=list(counts.values()), hole=0.55,
                                marker=dict(colors=[PRIORITY[k]["color"] for k, v in PRIORITY.items() if v["label"] in counts])))
        fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)",
                           font=dict(color="#8B97A6"), showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================== TOP FOR YOU

elif page == "Top For You":
    st.markdown("## Top 5 Updates You Should Know Today")
    st.caption("Ranked specifically for your profile — not just the most recent news.")
    for i, (u, s) in enumerate(SCORED[:5], start=1):
        render_update_card(u, s, rank=i)

# ============================================================== GCP + AI

elif page == "GCP + AI":
    st.markdown("## GCP + AI")
    st.caption("Developments directly relevant to GCP data engineering — BigQuery, Vertex AI, Gemini, and related tooling.")
    gcp_items = [(u, s) for u, s in SCORED if u["is_gcp"] or u["tier"] == 1]
    for u, s in gcp_items:
        render_update_card(u, s)
    if not gcp_items:
        st.info("No GCP-tagged updates right now.")

# ============================================================== AI UPDATES

elif page == "AI Updates":
    st.markdown("## AI Updates")
    st.caption("Broader AI developments, ranked by relevance to your profile rather than recency.")
    f1, f2 = st.columns(2)
    tier_filter = f1.selectbox("Tier", ["All tiers", "Tier 1", "Tier 2", "Tier 3", "Tier 4"])
    prio_filter = f2.selectbox("Priority", ["All priorities"] + [p["label"] for p in PRIORITY.values()])
    items = SCORED
    if tier_filter != "All tiers":
        t = int(tier_filter.split(" ")[1])
        items = [(u, s) for u, s in items if u["tier"] == t]
    if prio_filter != "All priorities":
        items = [(u, s) for u, s in items if PRIORITY[priority_for(s)]["label"] == prio_filter]
    st.caption(f"{len(items)} updates")
    for u, s in items:
        render_update_card(u, s)

# ============================================================== LEARNING ROADMAP

elif page == "Learning Roadmap":
    st.markdown("## 🎓 My AI Learning Roadmap")
    buckets = {"Learn Now": [], "Learn Next": [], "Explore Later": [], "Watch": []}
    for u, s in SCORED:
        pr = priority_for(s)
        bucket = {"must": "Learn Now", "important": "Learn Next", "explore": "Explore Later", "watch": "Watch"}[pr]
        buckets[bucket].append((u, s))

    for label in ["Learn Now", "Learn Next", "Explore Later"]:
        st.markdown(f"### {label}")
        items = buckets[label]
        if not items:
            st.caption("Nothing here right now.")
            continue
        for u, s in items:
            st.markdown(f'<div class="card"><b>{u["title"]}</b> '
                        f'<span class="faint">{u["category"]}</span><br>'
                        f'<span class="muted" style="font-size:13px;">{u["why_learn"]}</span><br>'
                        f'<span class="mono" style="font-size:13px; color:#4285F4;">Personal Relevance: {s:.0f}/100</span>'
                        f'</div>', unsafe_allow_html=True)

    with st.expander(f"Watch list ({len(buckets['Watch'])} items — tracked but not prioritized)"):
        for u, s in buckets["Watch"]:
            st.markdown(f"- **{u['title']}** — {s:.0f}/100")

# ============================================================== PROJECT IDEAS

elif page == "Project Ideas":
    st.markdown("## 💡 Projects I Can Build")
    st.caption("Practical project ideas inspired by this week's updates.")
    cols = st.columns(3)
    for col, proj in zip(cols, PROJECT_IDEAS):
        with col:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"### {proj['icon']} {proj['name']}")
            st.markdown(f'<span class="muted">{proj["description"]}</span>', unsafe_allow_html=True)
            for b in proj["bullets"]:
                st.markdown(f"- {b}")
            st.markdown('</div>', unsafe_allow_html=True)

# ============================================================== WEEKLY REPORT

elif page == "Weekly Report":
    st.markdown("## 📊 My AI & Data Engineering Weekly Report")
    st.caption("Generated live from this week's updates, weighted by your current profile.")
    generate = st.button("✨ Generate my weekly report")

    if generate:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            st.session_state.report_error = "No ANTHROPIC_API_KEY found. Set it as an environment variable or in .streamlit/secrets.toml."
            st.session_state.report = None
        else:
            with st.spinner("Generating your report…"):
                try:
                    import anthropic
                    client = anthropic.Anthropic(api_key=api_key)
                    payload = [dict(title=u["title"], category=u["category"], tier=u["tier"],
                                     source=u["source"], summary=u["summary"],
                                     personal_relevance=s, priority=PRIORITY[priority_for(s)]["label"],
                                     gcp_use=u["gcp_use"]) for u, s in SCORED]
                    profile = st.session_state.profile
                    weights = st.session_state.weights
                    prompt = f"""You are a personal AI Career Intelligence Assistant and GCP Data Engineering Advisor — not a generic AI news aggregator.

USER PROFILE:
Role: {profile['role']}
Primary expertise: {profile['expertise']}
AI experience: {profile['ai_experience']}

SCORING WEIGHTS CURRENTLY IN USE:
{json.dumps(weights)}

THIS WEEK'S UPDATES (already scored and ranked for this user, JSON):
{json.dumps(payload)}

Write "My AI & Data Engineering Weekly Report" with these exact sections, in plain text (no markdown headers, use simple line breaks and dashes):
1. Most Important Updates — top 5 developments with a one-line reason each.
2. What Changed in GCP? — the important GCP-specific developments.
3. What Changed in AI? — important broader AI developments relevant to data engineering.
4. What Should I Learn? — top 3 technologies, ranked, with a one-line reason each.
5. What Should I Build? — top 2 practical project ideas grounded in this week's updates.
6. Career Impact — a short paragraph on how this week's developments affect the skills expected from a modern GCP Data Engineer.

Every point must connect specifically to GCP + Data Engineering + AI — never generic statements like "AI is growing fast, so learn it."""
                    response = client.messages.create(
                        model="claude-sonnet-4-6",
                        max_tokens=1400,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    text = "".join(block.text for block in response.content if hasattr(block, "text"))
                    st.session_state.report = text
                    st.session_state.report_error = None
                except Exception as e:
                    st.session_state.report_error = str(e)
                    st.session_state.report = None

    if st.session_state.report:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="muted" style="white-space:pre-wrap; font-size:13.5px; line-height:1.65;">{st.session_state.report}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state.report_error:
        st.error(f"Couldn't generate the report: {st.session_state.report_error}")

# ============================================================== PROFILE

elif page == "Profile":
    st.markdown("## ⚙️ Profile")
    st.caption("Your role and expertise personalize every 'Why should I learn this?' explanation across the app.")
    p = st.session_state.profile
    p["role"] = st.text_input("Role", p["role"])
    p["expertise"] = st.text_area("Primary expertise", p["expertise"])
    p["ai_experience"] = st.text_area("AI experience", p["ai_experience"])

    st.markdown("### Personal Relevance Score weights")
    st.caption("These weights drive every ranking in the app. Defaults match the GCP Data Engineer profile — adjust and see everything re-rank.")
    w = st.session_state.weights
    cols = st.columns(3)
    keys = list(w.keys())
    for i, key in enumerate(keys):
        with cols[i % 3]:
            w[key] = st.slider(WEIGHT_LABELS[key], 0, 100, w[key], key=f"w_{key}")
    total = sum(w.values())
    if total != 100:
        st.warning(f"Weights currently sum to {total}%, not 100% — scores are normalized automatically, but you may want them to add up to 100 for clarity.")
    if st.button("Reset weights to default"):
        st.session_state.weights = dict(DEFAULT_WEIGHTS)
        st.rerun()
