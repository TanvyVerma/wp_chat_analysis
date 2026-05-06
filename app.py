import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ChatLens · WhatsApp Analytics",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True
if 'analysis_run' not in st.session_state:
    st.session_state.analysis_run = False


# ── CSS INJECTION ─────────────────────────────────────────────────────────────
def inject_css(dark):
    if dark:
        bg         = "#0d0f14"
        surface2   = "#1e2330"
        border     = "#2a2f3d"
        accent     = "#6c63ff"
        accent2    = "#00d4aa"
        accent3    = "#ff6b6b"
        text_prim  = "#f0f2f8"
        text_sec   = "#8b92a8"
        text_muted = "#4a5068"
        sidebar_bg = "#0f1117"
        metric_bg  = "#1e2330"
        positive   = "#00d4aa"
        negative   = "#ff6b6b"
        neutral_c  = "#6c63ff"
        chart_bg   = "#161a23"
        chart_text = "#8b92a8"
        chart_grid = "#2a2f3d"
    else:
        bg         = "#f5f6fa"
        surface2   = "#f0f2f8"
        border     = "#e2e6f0"
        accent     = "#5b50f0"
        accent2    = "#00b894"
        accent3    = "#e84545"
        text_prim  = "#1a1d2e"
        text_sec   = "#5a607a"
        text_muted = "#a0a8c0"
        sidebar_bg = "#eef0f7"
        metric_bg  = "#f0f2f8"
        positive   = "#00b894"
        negative   = "#e84545"
        neutral_c  = "#5b50f0"
        chart_bg   = "#ffffff"
        chart_text = "#5a607a"
        chart_grid = "#e2e6f0"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap');

    :root {{
        --bg:{bg}; --surface2:{surface2}; --border:{border};
        --accent:{accent}; --accent2:{accent2}; --accent3:{accent3};
        --text-prim:{text_prim}; --text-sec:{text_sec}; --text-muted:{text_muted};
        --sidebar-bg:{sidebar_bg}; --metric-bg:{metric_bg};
        --positive:{positive}; --negative:{negative}; --neutral:{neutral_c};
        --chart-bg:{chart_bg}; --chart-text:{chart_text}; --chart-grid:{chart_grid};
    }}

    html, body, [class*="css"] {{
        font-family: 'DM Sans', sans-serif !important;
        background-color: var(--bg) !important;
        color: var(--text-prim) !important;
    }}
    .stApp {{ background-color: var(--bg) !important; }}

    section[data-testid="stSidebar"] {{
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border) !important;
    }}
    section[data-testid="stSidebar"] * {{ color: var(--text-prim) !important; }}

    [data-testid="stFileUploader"] {{
        background: var(--surface2) !important;
        border: 1.5px dashed var(--border) !important;
        border-radius: 12px !important;
    }}
    [data-testid="stSelectbox"] > div > div {{
        background: var(--surface2) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text-prim) !important;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, {accent}, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: 0.04em !important;
        padding: 0.65rem 1.5rem !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 20px {accent}44 !important;
        cursor: pointer !important;
    }}
    .stButton > button:hover {{
        opacity: 0.9 !important;
        box-shadow: 0 6px 28px {accent}66 !important;
    }}

    .stDownloadButton > button {{
        background: var(--surface2) !important;
        color: {accent} !important;
        border: 1px solid {accent} !important;
        border-radius: 10px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.2s !important;
    }}
    .stDownloadButton > button:hover {{
        background: {accent} !important;
        color: white !important;
    }}

    [data-testid="metric-container"] {{
        background: var(--metric-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
        padding: 1.2rem 1.4rem !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: var(--text-sec) !important;
        font-size: 11px !important;
        font-weight: 500 !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
    }}
    [data-testid="stMetricValue"] {{
        color: var(--text-prim) !important;
        font-family: 'Syne', sans-serif !important;
        font-size: 26px !important;
        font-weight: 700 !important;
    }}

    [data-testid="stDataFrame"] {{
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }}

    [data-testid="stTabs"] [role="tablist"] {{
        background: var(--surface2) !important;
        border-radius: 12px !important;
        padding: 4px !important;
        gap: 2px !important;
        border-bottom: none !important;
    }}
    [data-testid="stTabs"] [role="tab"] {{
        background: transparent !important;
        border: none !important;
        border-radius: 8px !important;
        color: var(--text-sec) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        padding: 0.4rem 0.85rem !important;
        transition: all 0.15s !important;
    }}
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
        background: {accent} !important;
        color: white !important;
    }}

    [data-testid="stAlert"] {{
        background: var(--surface2) !important;
        border: 1px solid var(--border) !important;
        border-left: 3px solid {accent2} !important;
        border-radius: 10px !important;
        color: var(--text-prim) !important;
    }}

    #MainMenu, footer, header {{ visibility: hidden; }}
    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px !important;
    }}
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: var(--bg); }}
    ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 99px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {accent}; }}
    </style>
    """, unsafe_allow_html=True)

    return dict(
        bg=bg, surface2=surface2, border=border,
        accent=accent, accent2=accent2, accent3=accent3,
        text_prim=text_prim, text_sec=text_sec, text_muted=text_muted,
        positive=positive, negative=negative, neutral_c=neutral_c,
        chart_bg=chart_bg, chart_text=chart_text, chart_grid=chart_grid
    )


C = inject_css(st.session_state.dark_mode)
AC, AC2, AC3 = C["accent"], C["accent2"], C["accent3"]
POS, NEG     = C["positive"], C["negative"]


# ── CHART THEME ───────────────────────────────────────────────────────────────
def style_fig(fig, ax_or_axes=None):
    fig.patch.set_facecolor(C["chart_bg"])
    axes = ax_or_axes if ax_or_axes is not None else fig.get_axes()
    if not isinstance(axes, list):
        axes = [axes]
    for ax in axes:
        ax.set_facecolor(C["chart_bg"])
        ax.tick_params(colors=C["chart_text"], labelsize=9)
        ax.xaxis.label.set_color(C["chart_text"])
        ax.yaxis.label.set_color(C["chart_text"])
        for spine in ax.spines.values():
            spine.set_edgecolor(C["chart_grid"])
        ax.grid(color=C["chart_grid"], linewidth=0.5, alpha=0.6, zorder=0)
    return fig


# ── UI HELPERS ────────────────────────────────────────────────────────────────
def section_header(icon, title, subtitle=None):
    sub = f"<p style='margin:4px 0 0;color:var(--text-sec);font-size:13px;font-weight:300;'>{subtitle}</p>" if subtitle else ""
    st.markdown(f"""
    <div style='margin:2.5rem 0 1.2rem;display:flex;align-items:center;gap:14px;'>
        <div style='width:42px;height:42px;background:linear-gradient(135deg,{AC}22,{AC2}22);
                    border:1px solid {AC}44;border-radius:12px;display:flex;
                    align-items:center;justify-content:center;font-size:18px;flex-shrink:0;'>{icon}</div>
        <div>
            <h2 style='margin:0;font-family:Syne,sans-serif;font-size:20px;font-weight:700;
                       color:var(--text-prim);letter-spacing:-0.02em;'>{title}</h2>
            {sub}
        </div>
    </div>""", unsafe_allow_html=True)


def stat_card(label, value, color, icon=""):
    st.markdown(f"""
    <div style='background:var(--metric-bg);border:1px solid var(--border);border-radius:14px;
                padding:1.2rem 1.4rem;border-top:3px solid {color};height:100%;'>
        <div style='font-size:11px;font-weight:500;letter-spacing:0.1em;text-transform:uppercase;
                    color:var(--text-sec);margin-bottom:8px;'>{icon} {label}</div>
        <div style='font-family:Syne,sans-serif;font-size:24px;font-weight:700;
                    color:var(--text-prim);word-break:break-word;'>{value}</div>
    </div>""", unsafe_allow_html=True)


def divider():
    st.markdown("<hr style='border:none;border-top:1px solid var(--border);margin:2rem 0;'>",
                unsafe_allow_html=True)


def badge(text, color):
    return (f"<span style='background:{color}22;color:{color};border:1px solid {color}44;"
            f"border-radius:99px;padding:2px 10px;font-size:11px;font-weight:500;'>{text}</span>")


def sub_label(text):
    st.markdown(f"<div style='font-size:12px;font-weight:500;letter-spacing:0.08em;"
                f"text-transform:uppercase;color:var(--text-sec);margin-bottom:10px;'>{text}</div>",
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style='padding:0.5rem 0 1rem;'>
        <div style='display:flex;align-items:center;gap:10px;'>
            <div style='width:36px;height:36px;background:linear-gradient(135deg,{AC},{AC2});
                        border-radius:10px;display:flex;align-items:center;
                        justify-content:center;font-size:16px;'>💬</div>
            <div>
                <div style='font-family:Syne,sans-serif;font-size:17px;font-weight:800;
                            letter-spacing:-0.02em;color:var(--text-prim);'>ChatLens</div>
                <div style='font-size:10px;color:var(--text-muted);letter-spacing:0.08em;
                            text-transform:uppercase;'>WhatsApp Analytics</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Theme toggle
    mode_label = "☀️  Light Mode" if st.session_state.dark_mode else "🌙  Dark Mode"
    if st.button(mode_label, key="theme_btn"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.session_state.analysis_run = False
        st.rerun()

    st.markdown(f"<div style='height:1px;background:var(--border);margin:1rem 0;'></div>",
                unsafe_allow_html=True)

    st.markdown("<div style='font-size:11px;font-weight:500;letter-spacing:0.1em;"
                "text-transform:uppercase;color:var(--text-muted);margin-bottom:8px;'>Upload Chat</div>",
                unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload WhatsApp .txt export",
        type=["txt"],
        label_visibility="collapsed",
        key="file_uploader"
    )

    # Defaults
    df            = None
    selected_user = "Overall"
    fmt           = "android"

    if uploaded_file is not None:
        try:
            data = uploaded_file.getvalue().decode("utf-8")
            df   = preprocessor.preprocess(data)
        except Exception as e:
            st.error(f"Parse error: {e}")
            df = None

        if df is not None and not df.empty:
            fmt = df["chat_format"].iloc[0] if "chat_format" in df.columns else "android"
            fmt_color = AC2 if fmt == "ios" else AC
            st.markdown(
                f"<div style='margin:8px 0;'>"
                f"{badge(('iOS' if fmt=='ios' else 'Android') + ' detected', fmt_color)}"
                f"</div>",
                unsafe_allow_html=True
            )

            st.markdown(f"<div style='height:1px;background:var(--border);margin:0.75rem 0;'></div>",
                        unsafe_allow_html=True)
            st.markdown("<div style='font-size:11px;font-weight:500;letter-spacing:0.1em;"
                        "text-transform:uppercase;color:var(--text-muted);margin-bottom:8px;'>Analyse As</div>",
                        unsafe_allow_html=True)

            user_list = [u for u in df["user"].unique().tolist() if u != "group_notification"]
            user_list.sort()
            user_list.insert(0, "Overall")
            selected_user = st.selectbox("Select user", user_list, label_visibility="collapsed")

            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            if st.button("Run Analysis →", key="run_btn"):
                st.session_state.analysis_run = True

            # Quick stats mini cards
            total_msgs  = df.shape[0]
            total_users = df["user"].nunique()
            st.markdown(f"""
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:1rem;'>
                <div style='background:var(--surface2);border:1px solid var(--border);
                            border-radius:10px;padding:10px 12px;text-align:center;'>
                    <div style='font-family:Syne,sans-serif;font-size:18px;font-weight:700;
                                color:{AC};'>{total_msgs:,}</div>
                    <div style='font-size:10px;color:var(--text-muted);text-transform:uppercase;
                                letter-spacing:0.06em;margin-top:2px;'>Messages</div>
                </div>
                <div style='background:var(--surface2);border:1px solid var(--border);
                            border-radius:10px;padding:10px 12px;text-align:center;'>
                    <div style='font-family:Syne,sans-serif;font-size:18px;font-weight:700;
                                color:{AC2};'>{total_users}</div>
                    <div style='font-size:10px;color:var(--text-muted);text-transform:uppercase;
                                letter-spacing:0.06em;margin-top:2px;'>Members</div>
                </div>
            </div>""", unsafe_allow_html=True)

        else:
            st.warning("Could not parse file. Make sure it's a WhatsApp .txt export.")


# ══════════════════════════════════════════════════════════════════════════════
# HERO — no file uploaded
# ══════════════════════════════════════════════════════════════════════════════
if uploaded_file is None:
    st.session_state.analysis_run = False
    st.markdown(f"""
    <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;
                min-height:72vh;text-align:center;padding:2rem;'>
        <div style='width:76px;height:76px;background:linear-gradient(135deg,{AC},{AC2});
                    border-radius:22px;display:flex;align-items:center;justify-content:center;
                    font-size:34px;margin-bottom:1.5rem;box-shadow:0 16px 48px {AC}44;'>💬</div>
        <h1 style='font-family:Syne,sans-serif;font-size:clamp(40px,6vw,62px);font-weight:800;
                   letter-spacing:-0.03em;margin:0 0 0.5rem;color:var(--text-prim);line-height:1.05;'>
            Chat<span style='color:{AC};'>Lens</span>
        </h1>
        <p style='font-size:17px;color:var(--text-sec);font-weight:300;max-width:460px;
                  line-height:1.65;margin:0 0 2rem;'>
            Turn your WhatsApp conversations into beautiful, actionable analytics.
        </p>
        <div style='display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-bottom:2.5rem;'>
            {''.join([
                f"<span style='background:var(--surface2);border:1px solid var(--border);"
                f"border-radius:99px;padding:6px 16px;font-size:12px;color:var(--text-sec);'>✦ {f}</span>"
                for f in ["Sentiment Analysis","Response Time","Topic Modeling",
                          "PDF Export","Language Detection","Dark & Light Mode"]
            ])}
        </div>
        <div style='background:var(--surface2);border:1px dashed var(--border);border-radius:14px;
                    padding:1.2rem 2rem;max-width:380px;'>
            <div style='font-size:13px;color:var(--text-muted);'>
                ← Upload your
                <code style="background:var(--border);padding:1px 6px;border-radius:4px;
                             font-size:12px;">.txt</code>
                WhatsApp export from the sidebar
            </div>
        </div>
    </div>""", unsafe_allow_html=True)
    st.stop()


# ── File loaded but analysis not run yet ──────────────────────────────────────
if df is None or not st.session_state.analysis_run:
    st.markdown(f"""
    <div style='display:flex;flex-direction:column;align-items:center;
                justify-content:center;min-height:60vh;text-align:center;'>
        <div style='font-size:52px;margin-bottom:1.2rem;'>📂</div>
        <h2 style='font-family:Syne,sans-serif;font-size:22px;font-weight:700;
                   color:var(--text-prim);margin:0 0 0.5rem;'>
            {'Chat file loaded!' if df is not None else 'Upload a file to begin'}
        </h2>
        <p style='color:var(--text-sec);font-size:14px;margin:0;line-height:1.7;'>
            {'Select a user and hit <b>Run Analysis →</b> in the sidebar.' if df is not None
             else 'Use the sidebar on the left to upload your WhatsApp .txt export.'}
        </p>
    </div>""", unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style='display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;
            gap:12px;padding-bottom:1.5rem;border-bottom:1px solid var(--border);margin-bottom:0.5rem;'>
    <div>
        <div style='font-size:11px;color:var(--text-muted);letter-spacing:0.1em;
                    text-transform:uppercase;margin-bottom:4px;'>Analysis Report</div>
        <h1 style='font-family:Syne,sans-serif;font-size:28px;font-weight:800;
                   letter-spacing:-0.02em;margin:0;color:var(--text-prim);'>
            {selected_user if selected_user != "Overall" else "All Participants"}
        </h1>
    </div>
    <div style='display:flex;gap:8px;align-items:center;'>
        {badge("Live Report", AC2)}
        {badge("iOS" if fmt == "ios" else "Android", AC)}
    </div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tabs = st.tabs(["📊 Overview", "😊 Sentiment", "⚡ Response Time",
                "📅 Timelines", "🧠 Deep Analysis", "📄 Export"])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 · OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    section_header("🔢", "Key Statistics", "High-level numbers from the conversation")

    num_msg, num_word, num_media, num_links = helper.fetch_stats(selected_user, df)
    c1, c2, c3, c4 = st.columns(4)
    with c1: stat_card("Messages", f"{num_msg:,}",   AC,        "💬")
    with c2: stat_card("Words",    f"{num_word:,}",   AC2,       "📝")
    with c3: stat_card("Media",    f"{num_media:,}",  AC3,       "📸")
    with c4: stat_card("Links",    f"{num_links:,}",  "#f59e0b", "🔗")

    divider()
    section_header("📌", "Activity Overview", "When and how often the chat is active")

    c1, c2 = st.columns(2)
    with c1:
        sub_label("Most active days")
        busy_day  = helper.week_activity_map(selected_user, df)
        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        busy_day  = busy_day.reindex([d for d in day_order if d in busy_day.index])
        fig, ax   = plt.subplots(figsize=(6, 3.2))
        bcolors   = [AC2 if i == int(busy_day.values.argmax()) else AC for i in range(len(busy_day))]
        ax.bar(busy_day.index, busy_day.values, color=bcolors, alpha=0.85, width=0.6, zorder=3)
        ax.set_ylabel("Messages", fontsize=9)
        plt.xticks(rotation=30, ha="right")
        style_fig(fig, ax); st.pyplot(fig); plt.close()

    with c2:
        sub_label("Most active months")
        busy_month = helper.month_activity_map(selected_user, df)
        fig, ax    = plt.subplots(figsize=(6, 3.2))
        bcolors2   = [AC3 if i == int(busy_month.values.argmax()) else AC for i in range(len(busy_month))]
        ax.bar(busy_month.index, busy_month.values, color=bcolors2, alpha=0.85, width=0.6, zorder=3)
        ax.set_ylabel("Messages", fontsize=9)
        plt.xticks(rotation=30, ha="right")
        style_fig(fig, ax); st.pyplot(fig); plt.close()

    divider()
    section_header("🔥", "Weekly Activity Heatmap", "Message density by day and hour")
    user_heatmap = helper.activity_heatmap(selected_user, df)
    fig, ax = plt.subplots(figsize=(14, 4))
    sns.heatmap(user_heatmap, ax=ax,
                cmap="RdPu" if st.session_state.dark_mode else "BuPu",
                linewidths=0.3, linecolor=C["chart_grid"], cbar_kws={"shrink": 0.6})
    ax.set_xlabel("Hour Period", fontsize=9)
    ax.set_ylabel("Day", fontsize=9)
    style_fig(fig, ax); st.pyplot(fig); plt.close()

    if selected_user == "Overall":
        divider()
        section_header("🏆", "Most Active Users", "Top contributors to the conversation")
        x, new_df = helper.most_busy_users(df)
        c1, c2 = st.columns([3, 2])
        with c1:
            fig, ax   = plt.subplots(figsize=(6, 3.5))
            bcolors3  = [AC2 if i == 0 else AC for i in range(len(x))]
            ax.barh(x.index[::-1], x.values[::-1], color=bcolors3[::-1], alpha=0.9, zorder=3)
            ax.set_xlabel("Messages", fontsize=9)
            style_fig(fig, ax); st.pyplot(fig); plt.close()
        with c2:
            st.dataframe(new_df, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 · SENTIMENT
# ════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    section_header("😊", "Sentiment Analysis", "Emotional tone of messages over time")

    counts  = helper.sentiment_counts(selected_user, df)
    pos_n   = counts.get("Positive", 0)
    neu_n   = counts.get("Neutral",  0)
    neg_n   = counts.get("Negative", 0)
    total_s = max(pos_n + neu_n + neg_n, 1)

    c1, c2, c3 = st.columns(3)
    with c1: stat_card("Positive", f"{pos_n:,}  ({round(pos_n/total_s*100)}%)", POS,             "😊")
    with c2: stat_card("Neutral",  f"{neu_n:,}  ({round(neu_n/total_s*100)}%)", C["neutral_c"], "😐")
    with c3: stat_card("Negative", f"{neg_n:,}  ({round(neg_n/total_s*100)}%)", NEG,             "😞")

    divider()
    section_header("📈", "Daily Sentiment Trend", "7-day rolling average of positivity score")
    trend = helper.daily_sentiment_trend(selected_user, df)
    if not trend.empty:
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(trend["date"], trend["rolling_avg"],   color=AC2, linewidth=2,   zorder=4, label="7-day avg")
        ax.plot(trend["date"], trend["avg_sentiment"], color=AC,  linewidth=0.7, alpha=0.4, zorder=3, label="Daily")
        ax.fill_between(trend["date"], trend["rolling_avg"], 0,
                        where=(trend["rolling_avg"] >= 0), alpha=0.12, color=POS, zorder=2)
        ax.fill_between(trend["date"], trend["rolling_avg"], 0,
                        where=(trend["rolling_avg"] < 0),  alpha=0.12, color=NEG, zorder=2)
        ax.axhline(0, color=C["chart_grid"], linewidth=1, linestyle="--")
        ax.set_ylabel("Sentiment Score", fontsize=9)
        ax.legend(fontsize=9, framealpha=0)
        plt.xticks(rotation=30, ha="right")
        style_fig(fig, ax); st.pyplot(fig); plt.close()

    if selected_user == "Overall":
        divider()
        section_header("🏅", "User Sentiment Ranking", "Who sends the most positive messages?")
        sent_summary = helper.user_sentiment_summary(df)
        if not sent_summary.empty:
            c1, c2 = st.columns([2, 3])
            with c1:
                st.dataframe(sent_summary, use_container_width=True, hide_index=True)
            with c2:
                fig, ax = plt.subplots(figsize=(6, max(3, len(sent_summary) * 0.55)))
                bcolors = [POS if v >= 0 else NEG for v in sent_summary["avg_sentiment"]]
                ax.barh(sent_summary["user"], sent_summary["avg_sentiment"],
                        color=bcolors, alpha=0.85, zorder=3)
                ax.axvline(0, color=C["chart_grid"], linewidth=1)
                ax.set_xlabel("Avg Sentiment Score", fontsize=9)
                style_fig(fig, ax); st.pyplot(fig); plt.close()


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 · RESPONSE TIME
# ════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    section_header("⚡", "Response Time Analysis", "How quickly people reply in the conversation")

    rt_df, avg_rt = helper.response_time_analysis(df)

    if not avg_rt.empty:
        fastest = avg_rt.iloc[0]
        slowest = avg_rt.iloc[-1]
        max_gap, gap_start, gap_end = helper.longest_silence(df)

        c1, c2, c3 = st.columns(3)
        with c1: stat_card("Fastest Responder", str(fastest["user"]),  AC2,       "🚀")
        with c2: stat_card("Slowest Responder", str(slowest["user"]),  AC3,       "🐢")
        with c3: stat_card("Longest Silence",   f"{max_gap}h",         "#f59e0b", "💤")

        divider()
        section_header("📊", "Avg Response Time per User",
                       "Lower is faster — gaps > 24h are excluded")
        c1, c2 = st.columns([3, 2])
        with c1:
            fig, ax   = plt.subplots(figsize=(7, max(3, len(avg_rt) * 0.65)))
            bar_c     = [AC2 if i == 0 else (AC3 if i == len(avg_rt)-1 else AC)
                         for i in range(len(avg_rt))]
            ax.barh(avg_rt["user"], avg_rt["avg_response_time_min"],
                    color=bar_c, alpha=0.85, zorder=3)
            ax.set_xlabel("Minutes", fontsize=9)
            for i, val in enumerate(avg_rt["avg_response_time_min"]):
                ax.text(val + 0.2, i, f"{val:.1f}m", va="center",
                        fontsize=8, color=C["chart_text"])
            style_fig(fig, ax); st.pyplot(fig); plt.close()
        with c2:
            st.dataframe(avg_rt, use_container_width=True, hide_index=True)

        divider()
        section_header("📉", "Response Time Distribution",
                       "Spread of all response times (95th percentile clipped)")
        fig, ax  = plt.subplots(figsize=(10, 3.5))
        clipped  = rt_df[rt_df["response_time_min"] < rt_df["response_time_min"].quantile(0.95)]
        ax.hist(clipped["response_time_min"], bins=40,
                color=AC, alpha=0.75, edgecolor=C["chart_grid"], zorder=3)
        median_rt = clipped["response_time_min"].median()
        ax.axvline(median_rt, color=AC2, linewidth=1.5, linestyle="--",
                   label=f"Median: {median_rt:.1f}m")
        ax.set_xlabel("Response Time (minutes)", fontsize=9)
        ax.set_ylabel("Frequency", fontsize=9)
        ax.legend(fontsize=9, framealpha=0)
        style_fig(fig, ax); st.pyplot(fig); plt.close()

        if gap_start and gap_end:
            st.markdown(f"""
            <div style='background:var(--surface2);border:1px solid var(--border);
                        border-left:3px solid #f59e0b;border-radius:10px;
                        padding:1rem 1.2rem;margin-top:1rem;'>
                <div style='font-size:11px;font-weight:500;letter-spacing:0.08em;
                            text-transform:uppercase;color:#f59e0b;margin-bottom:6px;'>
                    💤 Longest Silence
                </div>
                <div style='font-size:15px;font-weight:500;color:var(--text-prim);'>
                    {max_gap} hours with no messages
                </div>
                <div style='font-size:12px;color:var(--text-sec);margin-top:4px;'>
                    From <b>{gap_start.strftime("%d %b %Y, %H:%M")}</b>
                    → <b>{gap_end.strftime("%d %b %Y, %H:%M")}</b>
                </div>
            </div>""", unsafe_allow_html=True)

        divider()
        section_header("🕐", "Hourly Response Patterns",
                       "Which hours see the quickest replies?")
        if not rt_df.empty and "responder" in rt_df.columns:
            # merge hour from original df
            df_with_hour = df[df["user"] != "group_notification"].copy()
            df_with_hour = df_with_hour.sort_values("date").reset_index(drop=True)
            hours = []
            for i in range(1, len(df_with_hour)):
                if df_with_hour.loc[i, "user"] != df_with_hour.loc[i-1, "user"]:
                    delta = (df_with_hour.loc[i, "date"] - df_with_hour.loc[i-1, "date"]).total_seconds() / 60
                    if 0 < delta < 1440:
                        hours.append(df_with_hour.loc[i, "hour"])

            if hours:
                hour_series = pd.Series(hours)
                hourly_avg  = hour_series.value_counts().sort_index()
                fig, ax = plt.subplots(figsize=(12, 3))
                bar_c   = [AC2 if v == hourly_avg.max() else AC for v in hourly_avg.values]
                ax.bar(hourly_avg.index, hourly_avg.values, color=bar_c, alpha=0.85, zorder=3)
                ax.set_xlabel("Hour of Day", fontsize=9)
                ax.set_ylabel("Replies", fontsize=9)
                ax.set_xticks(range(0, 24))
                style_fig(fig, ax); st.pyplot(fig); plt.close()
    else:
        st.info("Not enough data for response time analysis. Needs a multi-user conversation.")


# ════════════════════════════════════════════════════════════════════════════
# TAB 4 · TIMELINES
# ════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    section_header("📅", "Message Timelines", "How messaging patterns evolved over time")

    c1, c2 = st.columns(2)
    with c1:
        sub_label("Monthly")
        timeline = helper.monthly_timeline(selected_user, df)
        if not timeline.empty:
            fig, ax = plt.subplots(figsize=(6, 3.5))
            ax.plot(range(len(timeline)), timeline["message"],
                    color=AC, linewidth=2, marker="o", markersize=4,
                    markerfacecolor=AC2, zorder=4)
            ax.fill_between(range(len(timeline)), timeline["message"], alpha=0.08, color=AC)
            ax.set_xticks(range(len(timeline)))
            ax.set_xticklabels(timeline["time"], rotation=45, ha="right", fontsize=8)
            ax.set_ylabel("Messages", fontsize=9)
            style_fig(fig, ax); st.pyplot(fig); plt.close()
        else:
            st.info("No monthly data")

    with c2:
        sub_label("Daily")
        daily_tl = helper.daily_timeline(selected_user, df)
        if not daily_tl.empty:
            fig, ax = plt.subplots(figsize=(6, 3.5))
            ax.plot(daily_tl["only_date"], daily_tl["message"],
                    color=AC2, linewidth=1.2, alpha=0.9, zorder=4)
            ax.fill_between(daily_tl["only_date"], daily_tl["message"],
                            alpha=0.08, color=AC2)
            plt.xticks(rotation=45, ha="right", fontsize=8)
            ax.set_ylabel("Messages", fontsize=9)
            style_fig(fig, ax); st.pyplot(fig); plt.close()
        else:
            st.info("No daily data")

    divider()
    section_header("🔥", "Conversation Streaks", "Consecutive days with at least one message")
    max_streak, curr_streak, _ = helper.conversation_streaks(selected_user, df)
    c1, c2 = st.columns(2)
    with c1: stat_card("Longest Streak", f"{max_streak} days", AC,  "🏆")
    with c2: stat_card("Current Streak", f"{curr_streak} days", AC2, "📅")


# ════════════════════════════════════════════════════════════════════════════
# TAB 5 · DEEP ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    section_header("☁️", "Word Cloud", "Most frequently used words")
    try:
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(df_wc, interpolation="bilinear")
        ax.axis("off")
        fig.patch.set_facecolor(C["chart_bg"])
        st.pyplot(fig); plt.close()
    except Exception as e:
        st.warning(f"Word cloud error: {e}")

    divider()
    section_header("🔠", "Most Common Words", "Top 20 words excluding stop words")
    most_common_df = helper.most_common_words(selected_user, df)
    if not most_common_df.empty:
        fig, ax   = plt.subplots(figsize=(8, 5))
        bcolors   = [AC if i % 2 == 0 else AC2 for i in range(len(most_common_df))]
        ax.barh(most_common_df[0], most_common_df[1], color=bcolors, alpha=0.85, zorder=3)
        ax.set_xlabel("Count", fontsize=9)
        ax.invert_yaxis()
        style_fig(fig, ax); st.pyplot(fig); plt.close()

    divider()
    section_header("😄", "Emoji Analysis", "Most used emojis in the chat")
    emoji_df = helper.emoji_helper(selected_user, df)
    if not emoji_df.empty:
        c1, c2 = st.columns([2, 3])
        with c1:
            st.dataframe(emoji_df.head(20), use_container_width=True, hide_index=True)
        with c2:
            fig, ax = plt.subplots(figsize=(5, 5))
            pie_colors = [AC, AC2, AC3, "#f59e0b", "#8b5cf6", "#ec4899", "#14b8a6", "#f97316"]
            wedges, texts, autotexts = ax.pie(
                emoji_df[1].head(8), labels=emoji_df[0].head(8),
                autopct="%0.1f%%", colors=pie_colors,
                pctdistance=0.75, startangle=90,
                wedgeprops=dict(linewidth=2, edgecolor=C["chart_bg"])
            )
            for at in autotexts:
                at.set_color(C["chart_bg"]); at.set_fontsize(9)
            for t in texts:
                t.set_color(C["chart_text"]); t.set_fontsize(10)
            fig.patch.set_facecolor(C["chart_bg"])
            st.pyplot(fig); plt.close()

    divider()
    section_header("🌐", "Language Distribution", "Detected languages across all messages")
    lang_df = helper.language_distribution(selected_user, df)
    if not lang_df.empty:
        c1, c2 = st.columns([2, 3])
        with c1:
            st.dataframe(lang_df, use_container_width=True, hide_index=True)
        with c2:
            top_lang = lang_df[lang_df["language"] != "unknown"].head(6)
            if not top_lang.empty:
                fig, ax = plt.subplots(figsize=(5, 4))
                ax.pie(top_lang["count"], labels=top_lang["language"], autopct="%0.1f%%",
                       colors=[AC, AC2, AC3, "#f59e0b", "#8b5cf6", "#ec4899"],
                       startangle=90,
                       wedgeprops=dict(linewidth=2, edgecolor=C["chart_bg"]))
                fig.patch.set_facecolor(C["chart_bg"])
                st.pyplot(fig); plt.close()

    divider()
    section_header("🧠", "Topic Modeling", "Auto-detected conversation themes via LDA")
    with st.spinner("Running LDA analysis — may take a few seconds..."):
        topics_df, error = helper.topic_modeling(selected_user, df)
    if error:
        st.warning(error)
    elif topics_df is not None:
        for _, row in topics_df.iterrows():
            st.markdown(f"""
            <div style='background:var(--surface2);border:1px solid var(--border);
                        border-left:3px solid {AC};border-radius:10px;
                        padding:0.9rem 1.1rem;margin-bottom:8px;'>
                <div style='font-family:Syne,sans-serif;font-size:13px;font-weight:600;
                            color:{AC};margin-bottom:4px;'>{row["topic"]}</div>
                <div style='font-size:13px;color:var(--text-sec);'>{row["keywords"]}</div>
            </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 6 · EXPORT
# ════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    section_header("📄", "Export Report", "Download your full analysis as a PDF")

    st.markdown(f"""
    <div style='background:var(--surface2);border:1px solid var(--border);
                border-radius:14px;padding:1.5rem 1.8rem;margin-bottom:1.5rem;'>
        <div style='font-family:Syne,sans-serif;font-size:15px;font-weight:700;
                    color:var(--text-prim);margin-bottom:10px;'>What's included in the PDF</div>
        <div style='display:grid;grid-template-columns:1fr 1fr;gap:6px;'>
            {''.join([
                f"<div style='font-size:13px;color:var(--text-sec);'>✦ {item}</div>"
                for item in ["Key statistics summary", "Sentiment breakdown",
                             "Monthly timeline chart", "Sentiment trend chart",
                             "Top active users",       "Most common words"]
            ])}
        </div>
    </div>""", unsafe_allow_html=True)

    with st.spinner("Generating PDF..."):
        try:
            pdf_bytes = helper.generate_pdf_report(selected_user, df)
            st.download_button(
                label="⬇️  Download PDF Report",
                data=pdf_bytes,
                file_name=f"chatlens_{selected_user.lower().replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            st.success("Report is ready — click above to download.")
        except Exception as e:
            st.error(f"PDF failed: {e}  →  run: pip install fpdf2")