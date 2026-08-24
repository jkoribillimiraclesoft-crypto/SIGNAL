import os
import json
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# ============================================================== CONFIG

st.set_page_config(page_title="SIGNAL — AI Learning Intelligence", page_icon="📡", layout="wide")

PRIORITY = {
    "must": {"label": "Must Learn", "color": "#45D6C6", "order": 0},
    "important": {"label": "Important", "color": "#E8A23D", "order": 1},
    "explore": {"label": "Worth Exploring", "color": "#D9C558", "order": 2},
    "optional": {"label": "Optional", "color": "#5B6774", "order": 3},
}

# ============================================================== SAMPLE DATA

UPDATES = [
    dict(id=1, title="Anthropic ships native multi-agent orchestration API", source="Anthropic Blog",
         date="Aug 24, 2026", category="AI Agents", priority="must", difficulty="Intermediate", relevance=94,
         summary="A new API primitive lets developers spawn, coordinate, and hand off work between sub-agents without hand-rolled orchestration logic. Early adopters report a 3x reduction in glue code for multi-step workflows.",
         whats_new="Native support for spawning child agents with scoped tool access and automatic result aggregation back to a parent agent.",
         why_matters="Multi-agent patterns have been mostly bespoke until now. A first-party primitive lowers the bar for production agent systems considerably.",
         why_learn="Agentic architectures are becoming the default way serious AI products are built. Understanding orchestration patterns now positions you ahead of the shift from single-prompt apps to agent systems.",
         what_to_learn=["AI Agents", "Tool use / function calling", "Agent orchestration patterns"],
         priority_reason="Directly affects how production AI systems will be architected over the next 12 months.",
         prerequisites="Comfort with LLM tool-calling and basic async programming."),
    dict(id=2, title="MCP gains a standardized 'skills' extension across major clients", source="MCP Working Group",
         date="Aug 23, 2026", category="MCP", priority="must", difficulty="Intermediate", relevance=91,
         summary="A cross-vendor extension to the Model Context Protocol lets servers expose reusable, versioned 'skills' rather than raw tools, and is now supported by three major client implementations.",
         whats_new="A formal spec for packaging instructions + tools + resources as a single discoverable unit.",
         why_matters="Standardization reduces fragmentation between MCP clients and makes skill-based extensions portable across products.",
         why_learn="MCP is quickly becoming the common interface layer between models and external systems. Skills are the next abstraction layer on top of it.",
         what_to_learn=["Model Context Protocol", "MCP servers", "Skill packaging"],
         priority_reason="Foundational protocol change likely to affect any product that integrates external tools.",
         prerequisites="Basic familiarity with MCP server/client concepts."),
    dict(id=3, title="arXiv paper proposes a cheaper RAG evaluation harness", source="arXiv",
         date="Aug 22, 2026", category="RAG", priority="important", difficulty="Advanced", relevance=78,
         summary="Researchers introduce a sampling-based evaluation method that approximates full retrieval-quality benchmarks at roughly a tenth of the compute cost, with reported correlation above 0.9 to full evals.",
         whats_new="A stratified-sampling technique for scoring retrieval and generation quality without running the full benchmark suite.",
         why_matters="Cheap, frequent RAG evaluation makes it practical to catch retrieval regressions in CI rather than only in periodic audits.",
         why_learn="As RAG systems mature, evaluation is the bottleneck to trusting them in production. This is a rare cost-effective approach worth knowing.",
         what_to_learn=["RAG", "LLM evaluation", "Retrieval quality metrics"],
         priority_reason="High practical value for anyone running RAG in production, though the technique itself is niche.",
         prerequisites="Working knowledge of RAG pipelines and basic statistics."),
    dict(id=4, title="Open-weight 30B model matches proprietary models on coding benchmarks", source="GitHub Release Notes",
         date="Aug 22, 2026", category="Open Models", priority="important", difficulty="Beginner", relevance=82,
         summary="A newly released open-weight model reaches parity with closed frontier models on two widely used coding benchmarks while running on a single high-end consumer GPU.",
         whats_new="Open weights, training recipe, and eval harness released together, which is unusual for a model at this performance tier.",
         why_matters="Narrows the practical gap between open and closed models for coding use cases, expanding options for self-hosted deployments.",
         why_learn="Worth knowing what's achievable locally right now, especially if cost or data residency matters for your projects.",
         what_to_learn=["Open-weight models", "Local inference", "Coding benchmarks"],
         priority_reason="Meaningful for anyone evaluating self-hosted vs. API-based model strategy.",
         prerequisites="None — accessible to newcomers."),
    dict(id=5, title="Lightweight Rust vector database crosses 10k GitHub stars", source="GitHub Trending",
         date="Aug 21, 2026", category="Infrastructure", priority="explore", difficulty="Intermediate", relevance=61,
         summary="A minimal, embeddable vector database written in Rust is gaining traction for edge and single-binary deployments, trading some feature breadth for a tiny footprint.",
         whats_new="Single-binary deployment with no external dependencies, positioned as an alternative to heavier vector DB services.",
         why_matters="Lowers the barrier to adding retrieval to small or resource-constrained applications.",
         why_learn="Good to have on your radar if you build lightweight or edge-deployed RAG applications, though not urgent otherwise.",
         what_to_learn=["Vector databases", "Embedding storage", "Rust basics (optional)"],
         priority_reason="Useful niche tool rather than a broad shift — worth a bookmark, not a deep dive yet.",
         prerequisites="Basic understanding of embeddings and vector search."),
    dict(id=6, title="DeepMind publishes technique cutting inference cost ~40%", source="Google DeepMind Blog",
         date="Aug 21, 2026", category="Inference Optimization", priority="important", difficulty="Advanced", relevance=85,
         summary="A new speculative-decoding variant combined with dynamic batching reduces serving cost substantially with minimal quality loss, validated across three model sizes.",
         whats_new="A refined speculative decoding scheme paired with an adaptive batching scheduler.",
         why_matters="Serving cost is one of the biggest blockers to scaling AI features in production; a 40% reduction is significant at scale.",
         why_learn="Understanding inference optimization helps you reason about cost trade-offs even if you never implement this yourself.",
         what_to_learn=["Inference optimization", "Speculative decoding", "Serving infrastructure"],
         priority_reason="High impact for anyone operating models at scale, but implementation-heavy for most application developers.",
         prerequisites="Familiarity with how autoregressive decoding works."),
    dict(id=7, title="Hacker News debates whether agent frameworks are over-engineered", source="Hacker News",
         date="Aug 20, 2026", category="AI Agents", priority="explore", difficulty="Beginner", relevance=55,
         summary="A widely discussed thread argues many agent frameworks add abstraction without solving core reliability problems, with pushback from framework maintainers in the comments.",
         whats_new="No product news — a community discussion surfacing recurring critiques of agent framework complexity.",
         why_matters="Useful signal on where practitioners are hitting friction with current agent tooling.",
         why_learn="Worth skimming for perspective, not a technical skill to add to your queue on its own.",
         what_to_learn=["Agent framework trade-offs"],
         priority_reason="Informative context rather than an actionable skill.",
         prerequisites="None."),
    dict(id=8, title="Proposed observability standard for tracing agent tool calls", source="AI Newsletter Digest",
         date="Aug 20, 2026", category="AI Observability", priority="important", difficulty="Intermediate", relevance=76,
         summary="A vendor-neutral proposal defines a common trace format for agent tool calls, aiming to make debugging multi-step agent runs easier across different frameworks.",
         whats_new="A shared schema for logging tool calls, latencies, and intermediate agent state.",
         why_matters="Debugging agent behavior is currently ad hoc; a shared trace format would make tooling and postmortems far easier.",
         why_learn="As you build more agent systems, observability becomes essential rather than optional — good to get ahead of it.",
         what_to_learn=["AI observability", "Distributed tracing", "Agent debugging"],
         priority_reason="Early-stage but likely to matter more as agent systems grow in complexity.",
         prerequisites="Basic familiarity with agents and logging concepts."),
    dict(id=9, title="Fine-tuning recipe for domain-specific coding agents goes viral", source="Reddit r/LocalLLaMA",
         date="Aug 19, 2026", category="Fine-tuning", priority="explore", difficulty="Advanced", relevance=58,
         summary="A community-shared recipe for fine-tuning small models on internal codebases claims strong results for repo-specific coding assistants, though results are self-reported.",
         whats_new="A LoRA-based fine-tuning workflow tailored to single-repository coding assistants.",
         why_matters="Shows growing interest in cheap, narrow fine-tuning over general-purpose coding models.",
         why_learn="Relevant if you're curious about customizing models for a specific codebase, but claims aren't independently verified yet.",
         what_to_learn=["Fine-tuning", "LoRA", "Coding agents"],
         priority_reason="Promising but unverified — worth watching before investing significant time.",
         prerequisites="Experience with model fine-tuning workflows."),
    dict(id=10, title="EU updates guidance on high-risk AI system classification", source="Policy Bulletin",
         date="Aug 19, 2026", category="Policy", priority="optional", difficulty="Beginner", relevance=40,
         summary="Regulators clarify classification criteria for high-risk AI systems, with narrower carve-outs for certain developer tools than earlier drafts suggested.",
         whats_new="Refined thresholds for what counts as a high-risk AI system under existing guidance.",
         why_matters="Relevant mainly for teams shipping AI in regulated markets or high-risk categories.",
         why_learn="Low urgency unless your work touches regulated deployments directly.",
         what_to_learn=["AI policy basics"],
         priority_reason="Narrow relevance outside regulated industries.",
         prerequisites="None."),
    dict(id=11, title="Podcast: why prompt engineering is becoming 'context engineering'", source="AI Engineering Podcast",
         date="Aug 18, 2026", category="Prompt Engineering", priority="important", difficulty="Beginner", relevance=71,
         summary="A widely shared episode argues the hard part of building with LLMs has shifted from wording prompts to designing what context, tools, and memory the model sees at each step.",
         whats_new="A framing shift rather than a product release — but one that's shaping how teams describe their own work.",
         why_matters="Reflects a genuine shift in where engineering effort goes when building LLM applications.",
         why_learn="Useful mental model for prioritizing your own learning — context and retrieval design increasingly matter more than prompt wording alone.",
         what_to_learn=["Context engineering", "Prompt engineering", "Memory design"],
         priority_reason="Changes how you should prioritize learning time across related skills.",
         prerequisites="None."),
    dict(id=12, title="Meta releases multimodal benchmark suite for video understanding", source="Meta AI Blog",
         date="Aug 18, 2026", category="Multimodal", priority="explore", difficulty="Intermediate", relevance=63,
         summary="A new benchmark suite targets long-form video understanding, an area where current multimodal models still lag behind image and text performance.",
         whats_new="Standardized tasks for temporal reasoning and long-context video question answering.",
         why_matters="Gives the field a shared way to measure progress on a historically underbenchmarked capability.",
         why_learn="Good to track if multimodal or video applications are on your roadmap; not urgent otherwise.",
         what_to_learn=["Multimodal models", "Video understanding benchmarks"],
         priority_reason="Relevant to a specific application area rather than broadly applicable yet.",
         prerequisites="Basic familiarity with multimodal models."),
]

TRENDING = [
    dict(name="AI Agents", mentions=34, trend="up", priority="must",
         why="Core architecture shift across agent orchestration, frameworks, and observability news this week."),
    dict(name="Model Context Protocol", mentions=28, trend="up", priority="must",
         why="New standardized extensions are driving cross-vendor adoption."),
    dict(name="Context Engineering", mentions=19, trend="up", priority="important",
         why="Emerging as the reframing of prompt engineering for agentic systems."),
    dict(name="Open-Weight Models", mentions=22, trend="up", priority="important",
         why="Rapid quality gains are closing the gap with closed models."),
    dict(name="AI Observability", mentions=15, trend="up", priority="important",
         why="New tracing standards proposed as agent systems get harder to debug."),
    dict(name="Inference Optimization", mentions=13, trend="flat", priority="explore",
         why="Steady research output, no single breakout moment this week."),
]

TREND_DATA = [("Mon", 9), ("Tue", 12), ("Wed", 8), ("Thu", 15), ("Fri", 11), ("Sat", 6), ("Sun", 12)]

QUEUE = {
    "Learn Now": [
        dict(name="AI Agents", reason="Native orchestration APIs are making this the default architecture for production LLM apps."),
        dict(name="Model Context Protocol", reason="Rapidly becoming the standard interface between models and external tools."),
    ],
    "Learn Next": [
        dict(name="Context Engineering", reason="The skill set prompt engineering is evolving into as agent systems grow."),
        dict(name="AI Observability", reason="Will matter more as agent systems become harder to debug ad hoc."),
    ],
    "Keep Watching": [
        dict(name="Domain-Specific Fine-tuning", reason="Promising community results, not yet independently verified."),
        dict(name="Video Multimodal Benchmarks", reason="Relevant only if multimodal is on your roadmap."),
    ],
}

CATEGORIES = sorted({u["category"] for u in UPDATES})

# ============================================================== STYLE

DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
.stApp { background-color: #0A0E13; color: #E7EDF4; }
section[data-testid="stSidebar"] { background-color: #0D1218; border-right: 1px solid #232C38; }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; }
.mono { font-family: 'IBM Plex Mono', monospace; }
.card {
  background: #121821; border: 1px solid #232C38; border-radius: 12px;
  padding: 18px; margin-bottom: 14px;
}
.badge {
  display: inline-block; padding: 3px 10px; border-radius: 999px;
  font-size: 11px; font-weight: 600; font-family: 'IBM Plex Mono', monospace;
  letter-spacing: 0.3px; margin-right: 6px;
}
.tag {
  display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 12px;
  border: 1px solid #232C38; color: #E7EDF4; margin: 2px 4px 2px 0;
}
.muted { color: #8B97A6; }
.faint { color: #5B6774; font-size: 12px; font-family: 'IBM Plex Mono', monospace; }
.stat-box {
  background: #121821; border: 1px solid #232C38; border-radius: 10px;
  padding: 14px 16px; margin-bottom: 8px;
}
.stat-label { font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: #5B6774; letter-spacing: 0.5px; text-transform: uppercase;}
.stat-value { font-family: 'Space Grotesk', sans-serif; font-size: 26px; font-weight: 700; margin-top: 4px;}
</style>
"""

st.markdown(DARK_CSS, unsafe_allow_html=True)


def badge(priority_key):
    p = PRIORITY[priority_key]
    return f'<span class="badge" style="background:{p["color"]}; color:#06231F;">{p["label"]}</span>'


# ============================================================== SIDEBAR

with st.sidebar:
    st.markdown("### 📡 SIGNAL")
    st.caption("AI Learning Intelligence")
    page = st.radio("Navigate", ["Overview", "Latest Updates", "Trending Tech", "Learning Queue", "Profile"],
                     label_visibility="collapsed")
    st.divider()
    st.caption("Sample data for prototype purposes — connect live sources to go live.")

if "profile" not in st.session_state:
    st.session_state.profile = dict(
        skills="Python, JavaScript, REST APIs",
        languages="Python, TypeScript",
        interests="Backend engineering, developer tools",
        learning="AI Agents, MCP",
    )

# ============================================================== HEADER + DIGEST

col_a, col_b = st.columns([3, 1])
with col_a:
    st.markdown(f"## {page}")
with col_b:
    generate = st.button("✨ Generate today's briefing", use_container_width=True)

if generate:
    api_key = os.environ.get("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY", None) if hasattr(st, "secrets") else os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("No ANTHROPIC_API_KEY found. Set it as an environment variable or in .streamlit/secrets.toml before generating a briefing.")
    else:
        with st.spinner("Generating your briefing…"):
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                payload = [dict(title=u["title"], category=u["category"],
                                 priority=PRIORITY[u["priority"]]["label"], summary=u["summary"]) for u in UPDATES]
                profile = st.session_state.profile
                prompt = f"""You are an AI learning intelligence assistant. Based on this list of today's AI updates (JSON below) and the user's profile, write a short daily briefing.

USER PROFILE:
Skills: {profile['skills']}
Languages: {profile['languages']}
Career interests: {profile['interests']}
Currently learning: {profile['learning']}

UPDATES:
{json.dumps(payload)}

Write:
1. "Today's Most Important Updates" — 3-4 bullet points, each with what happened and why it matters, tailored to this user.
2. "What Should I Learn This Week?" — a ranked list of 3-5 topics with a one-line reason each, personalized to their profile.
Keep it concise and plain text, no markdown headers, use simple line breaks and dashes."""
                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}],
                )
                text = "".join(block.text for block in response.content if hasattr(block, "text"))
                st.session_state.digest = text
            except Exception as e:
                st.session_state.digest_error = str(e)

if st.session_state.get("digest"):
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**✨ AI Daily Briefing**")
        st.markdown(f'<div class="muted" style="white-space:pre-wrap; font-size:13.5px; line-height:1.6;">{st.session_state.digest}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Dismiss briefing"):
            st.session_state.digest = None
            st.rerun()

if st.session_state.get("digest_error"):
    st.error(f"Couldn't generate the briefing: {st.session_state.digest_error}")

st.markdown("---")

# ============================================================== OVERVIEW

if page == "Overview":
    c1, c2, c3, c4 = st.columns(4)
    for col, label, value, color in [
        (c1, "Updates Today", len(UPDATES), "#E7EDF4"),
        (c2, "Must Learn", sum(1 for u in UPDATES if u["priority"] == "must"), "#45D6C6"),
        (c3, "Trending Techs", len(TRENDING), "#E8A23D"),
        (c4, "Categories", len(CATEGORIES), "#E7EDF4"),
    ]:
        with col:
            st.markdown(f'<div class="stat-box"><div class="stat-label">{label}</div>'
                         f'<div class="stat-value" style="color:{color};">{value}</div></div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown("**Updates Over Time**")
        days = [d for d, _ in TREND_DATA]
        counts = [n for _, n in TREND_DATA]
        fig = go.Figure(go.Scatter(x=days, y=counts, mode="lines+markers",
                                    line=dict(color="#45D6C6", width=2), marker=dict(size=6, color="#45D6C6")))
        fig.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10),
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font=dict(color="#8B97A6"), xaxis=dict(gridcolor="#232C38"),
                           yaxis=dict(gridcolor="#232C38"))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("**Learning Priority Distribution**")
        counts = {p["label"]: sum(1 for u in UPDATES if u["priority"] == k) for k, p in PRIORITY.items()}
        fig = go.Figure(go.Pie(labels=list(counts.keys()), values=list(counts.values()), hole=0.55,
                                marker=dict(colors=[p["color"] for p in PRIORITY.values()])))
        fig.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10),
                           paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#8B97A6"), showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Updates by Category**")
    cat_counts = {cat: sum(1 for u in UPDATES if u["category"] == cat) for cat in CATEGORIES}
    fig = px.bar(x=list(cat_counts.keys()), y=list(cat_counts.values()))
    fig.update_traces(marker_color="#E8A23D")
    fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10),
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       font=dict(color="#8B97A6"), xaxis=dict(gridcolor="#232C38", title=""),
                       yaxis=dict(gridcolor="#232C38", title=""))
    st.plotly_chart(fig, use_container_width=True)

# ============================================================== FEED

elif page == "Latest Updates":
    f1, f2, f3 = st.columns([2, 1, 1])
    query = f1.text_input("Search", placeholder="Search updates or categories…", label_visibility="collapsed")
    cat_filter = f2.selectbox("Category", ["All categories"] + CATEGORIES, label_visibility="collapsed")
    prio_filter = f3.selectbox("Priority", ["All priorities"] + [p["label"] for p in PRIORITY.values()], label_visibility="collapsed")

    filtered = UPDATES
    if query:
        filtered = [u for u in filtered if query.lower() in u["title"].lower() or query.lower() in u["category"].lower()]
    if cat_filter != "All categories":
        filtered = [u for u in filtered if u["category"] == cat_filter]
    if prio_filter != "All priorities":
        filtered = [u for u in filtered if PRIORITY[u["priority"]]["label"] == prio_filter]
    filtered = sorted(filtered, key=lambda u: (PRIORITY[u["priority"]]["order"], -u["relevance"]))

    st.caption(f"{len(filtered)} updates")

    for u in filtered:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        top_l, top_r = st.columns([5, 1])
        with top_l:
            st.markdown(f'{badge(u["priority"])}<span class="faint">{u["category"]}</span>', unsafe_allow_html=True)
            st.markdown(f'#### {u["title"]}')
            st.markdown(f'<span class="muted">{u["summary"]}</span>', unsafe_allow_html=True)
            st.markdown(f'<span class="faint">{u["source"]} · {u["date"]}</span>', unsafe_allow_html=True)
        with top_r:
            st.metric("Relevance", f'{u["relevance"]}/100')

        with st.expander("View full details"):
            st.markdown(f"**Summary**  \n{u['summary']}")
            st.markdown(f"**What's New?**  \n{u['whats_new']}")
            st.markdown(f"**Why Does It Matter?**  \n{u['why_matters']}")
            st.markdown(f"**Why Should I Learn This?**  \n{u['why_learn']}")
            st.markdown("**What Should I Learn?**")
            st.markdown("".join(f'<span class="tag">{t}</span>' for t in u["what_to_learn"]), unsafe_allow_html=True)
            st.markdown(f"**Difficulty:** {u['difficulty']}")
            st.markdown(f"**Prerequisites:** {u['prerequisites']}")
            st.markdown(f"**Priority reason:** {u['priority_reason']}")
            st.link_button("Read original article ↗", "https://example.com")
        st.markdown('</div>', unsafe_allow_html=True)

    if not filtered:
        st.info("No updates match those filters.")

# ============================================================== TRENDING

elif page == "Trending Tech":
    for t in TRENDING:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        l, r = st.columns([4, 1])
        with l:
            st.markdown(f'#### {t["name"]}  {badge(t["priority"])}', unsafe_allow_html=True)
            st.markdown(f'<span class="muted">{t["why"]}</span>', unsafe_allow_html=True)
        with r:
            arrow = "↑" if t["trend"] == "up" else "→"
            st.metric("Mentions", t["mentions"], delta=("Rising" if t["trend"] == "up" else "Flat"))
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================== QUEUE

elif page == "Learning Queue":
    cols = st.columns(3)
    for col, (label, items) in zip(cols, QUEUE.items()):
        with col:
            st.markdown(f"#### {label}")
            for item in items:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f'**{item["name"]}**')
                st.markdown(f'<span class="muted" style="font-size:13px;">{item["reason"]}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# ============================================================== PROFILE

elif page == "Profile":
    st.caption("Used to personalize \"Why should I learn this?\" and the AI briefing above.")
    p = st.session_state.profile
    p["skills"] = st.text_input("Current technical skills", p["skills"])
    p["languages"] = st.text_input("Programming languages", p["languages"])
    p["interests"] = st.text_input("Career interests", p["interests"])
    p["learning"] = st.text_input("Technologies you want to learn", p["learning"])
