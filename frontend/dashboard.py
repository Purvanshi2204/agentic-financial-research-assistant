import streamlit as st
import requests
import io
import time
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors as rl_colors

st.set_page_config(page_title="FinResearch AI", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
#MainMenu,footer,header{visibility:hidden}
.stApp{background:#0D1520}
.main .block-container{padding:1.5rem 2rem;max-width:1200px}

/* ── Sidebar ── */
[data-testid="stSidebar"]{background:#0A1120!important;border-right:1px solid #1A2D40}
[data-testid="stSidebar"] *{color:#C8E0F4!important}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3{color:#FFFFFF!important}

/* ── Metrics ── */
[data-testid="metric-container"]{background:#0F1F32;border:1px solid #1A3050;border-radius:12px;padding:14px 16px}
[data-testid="metric-container"] label{color:#4A90B8!important;font-size:0.72rem!important;text-transform:uppercase;letter-spacing:.06em}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#FFFFFF!important;font-size:1.8rem!important;font-weight:700!important}
[data-testid="metric-container"] [data-testid="stMetricDelta"]{font-size:0.8rem!important}

/* ── Buttons ── */
.stButton>button{background:#0077CC;color:#FFFFFF;border:none;border-radius:8px;padding:.55rem 1.6rem;font-weight:700;font-size:.95rem;width:100%;letter-spacing:.02em}
.stButton>button:hover{background:#0088EE;box-shadow:0 0 0 3px rgba(0,120,200,.25)}
.stDownloadButton>button{background:#0F2A44!important;color:#40C4FF!important;border:1px solid #0077CC!important;border-radius:8px!important;width:100%;font-weight:700!important}
.stDownloadButton>button:hover{background:#1A3A55!important}

/* ── Inputs ── */
.stTextInput>div>div>input{background:#0F1F32!important;border:1px solid #1A3050!important;border-radius:8px!important;color:#FFFFFF!important;font-size:.95rem!important;caret-color:#40C4FF}
.stTextInput>div>div>input:focus{border-color:#0077CC!important;box-shadow:0 0 0 3px rgba(0,119,204,.2)!important}
.stTextInput>div>div>input::placeholder{color:#3A6080!important}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"]{background:#0A1628;border-radius:10px;padding:4px;gap:4px;border:1px solid #1A3050}
.stTabs [data-baseweb="tab"]{background:transparent;color:#5A90B8;border-radius:8px;padding:7px 22px;font-size:.88rem;font-weight:500}
.stTabs [aria-selected="true"]{background:#0077CC!important;color:#FFFFFF!important;font-weight:700!important}
.stTabs [data-baseweb="tab-border"]{display:none}
.stTabs [data-baseweb="tab-panel"]{padding-top:1.2rem}

/* ── Expander ── */
.streamlit-expanderHeader{background:#0F1F32!important;border:1px solid #1A3050!important;border-radius:8px!important;color:#FFFFFF!important;font-weight:600!important}
.streamlit-expanderContent{background:#080F1A!important;border:1px solid #1A3050!important;border-top:none!important}

/* ── Progress ── */
.stProgress>div>div{background:#0A1628!important}
.stProgress>div>div>div{background:linear-gradient(90deg,#0077CC,#00C4FF)!important;border-radius:99px!important}

/* ── Radio ── */
.stRadio label{color:#C8E0F4!important;font-size:.9rem!important}
.stRadio [data-baseweb="radio"] div{border-color:#0077CC!important}

/* ── Generic text ── */
p,li,span,div{color:#C8E0F4}
h1,h2,h3{color:#FFFFFF!important}
hr{border-color:#1A2D40!important}
.stMarkdown p{color:#C8E0F4;line-height:1.75}
label{color:#7ABCDD!important}

/* ── Custom components ── */
.onboard-banner{background:#0A1E35;border:1px solid #0077CC;border-radius:12px;padding:18px 20px;margin-bottom:.5rem}
.onboard-title{font-size:1rem;font-weight:700;color:#FFFFFF;margin-bottom:6px}
.onboard-body{font-size:.88rem;color:#7ABCDD;line-height:1.7;margin-bottom:12px}
.steps-row{display:flex;flex-wrap:wrap;gap:8px}
.step-pill{display:inline-flex;align-items:center;gap:6px;background:#0A1628;border:1px solid #1E4060;border-radius:99px;padding:4px 12px;font-size:.78rem;color:#40C4FF}
.step-num{width:18px;height:18px;border-radius:50%;background:#0077CC;color:#fff;font-size:.68rem;font-weight:700;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0}
.alert-ok{background:#051510;border:1px solid #0A4A28;border-left:4px solid #00E676;border-radius:0 8px 8px 0;padding:10px 16px;color:#00E676;font-size:.88rem;margin:.25rem 0}
.alert-warn{background:#150D00;border:1px solid #4A3000;border-left:4px solid #FFD740;border-radius:0 8px 8px 0;padding:10px 16px;color:#FFD740;font-size:.88rem;margin:.25rem 0}
.alert-danger{background:#150306;border:1px solid #4A0A14;border-left:4px solid #FF5252;border-radius:0 8px 8px 0;padding:10px 16px;color:#FF5252;font-size:.88rem;margin:.25rem 0}
.fin-card{background:#0F1F32;border:1px solid #1A3050;border-radius:12px;padding:16px 18px;margin-bottom:.75rem}
.sec-label{font-size:.72rem;font-weight:700;color:#2A7AAA;text-transform:uppercase;letter-spacing:.1em;padding-bottom:8px;border-bottom:1px solid #0F1F32;margin-bottom:12px}
.news-item{background:#080F1A;border:1px solid #122030;border-radius:8px;padding:9px 13px;margin-bottom:6px;font-size:.87rem;color:#C8E0F4;line-height:1.6;display:flex;align-items:flex-start;gap:9px}
.news-dot{width:7px;height:7px;border-radius:50%;background:#0077CC;flex-shrink:0;margin-top:5px}
.chip-ok{display:inline-block;background:#051510;border:1px solid #0A4A28;color:#00E676;border-radius:99px;padding:3px 11px;font-size:.75rem;margin:3px;font-weight:600}
.chip-bad{display:inline-block;background:#150306;border:1px solid #4A0A14;color:#FF5252;border-radius:99px;padding:3px 11px;font-size:.75rem;margin:3px;font-weight:600}
.company-badge{display:inline-flex;align-items:center;gap:8px;background:#0A1E35;border:1px solid #0077CC;color:#40C4FF;border-radius:8px;padding:5px 16px;font-size:.9rem;font-weight:700}
</style>
""", unsafe_allow_html=True)

# ── Mock Data ─────────────────────────────────────────────────────────────────
MOCK = {
    "apple": {"company":"Apple","ticker":"AAPL","sentiment_score":0.72,"sentiment_label":"Positive",
              "positive_pct":72,"neutral_pct":21,"negative_pct":7,
              "news_headlines":["Apple hits record quarterly revenue of $120B",
                                "iPhone 16 sales surpass analyst expectations",
                                "Apple expands AI features across product lineup",
                                "Apple stock reaches all-time high amid strong earnings",
                                "New MacBook with M4 chip receives rave reviews"],
              "stock_price":189.50,"stock_change":"+1.2%","stock_change_val":1.2,
              "market_cap":"2.94T","pe_ratio":28.5,"week_high":198.23,"week_low":142.10,
              "report_text":"Apple Inc. demonstrated strong positive momentum this week, driven by better-than-expected quarterly earnings and continued growth in its services segment. Sentiment across financial media remained largely bullish, with analysts highlighting the company's expanding AI integration as a key growth driver. Stock performance has been resilient, trading near all-time highs. Overall outlook remains positive with no significant risk flags detected."},
    "microsoft": {"company":"Microsoft","ticker":"MSFT","sentiment_score":0.65,"sentiment_label":"Positive",
                  "positive_pct":65,"neutral_pct":28,"negative_pct":7,
                  "news_headlines":["Microsoft Azure cloud revenue grows 28% year over year",
                                    "Copilot AI adoption accelerating across enterprise clients",
                                    "Microsoft acquires gaming studio for $1.2B",
                                    "Teams reaches 320 million daily active users",
                                    "Microsoft beats earnings estimates for third straight quarter"],
                  "stock_price":415.20,"stock_change":"+0.8%","stock_change_val":0.8,
                  "market_cap":"3.08T","pe_ratio":35.2,"week_high":430.82,"week_low":310.50,
                  "report_text":"Microsoft Corp. continues to show strong fundamentals, led by cloud and AI-driven growth. Azure's accelerating revenue growth and Copilot adoption signal a strong enterprise AI transition. Sentiment is broadly positive, though some analysts note valuation concerns at current price levels. No major risk flags detected. Well-positioned for continued outperformance."},
    "tesla": {"company":"Tesla","ticker":"TSLA","sentiment_score":0.28,"sentiment_label":"Neutral",
              "positive_pct":38,"neutral_pct":24,"negative_pct":38,
              "news_headlines":["Tesla misses delivery estimates for second consecutive quarter",
                                "Elon Musk announces new affordable EV model for 2025",
                                "Tesla faces increased competition from Chinese EV manufacturers",
                                "Autopilot investigation continues amid safety concerns",
                                "Tesla energy storage division posts record revenue"],
              "stock_price":245.30,"stock_change":"-2.1%","stock_change_val":-2.1,
              "market_cap":"0.78T","pe_ratio":52.8,"week_high":298.43,"week_low":138.80,
              "report_text":"Tesla Inc. presents a mixed picture this week. While the energy storage division continues to perform well, vehicle delivery shortfalls and increasing competition from Chinese EV manufacturers have weighed on sentiment. Regulatory scrutiny around Autopilot adds further uncertainty. Investors should monitor delivery figures closely in the upcoming quarter."},
}

def get_mock(company):
    return MOCK.get(company.lower().strip(), {
        "company":company,"ticker":"N/A","sentiment_score":0.5,"sentiment_label":"Neutral",
        "positive_pct":50,"neutral_pct":35,"negative_pct":15,
        "news_headlines":[f"No mock data for {company}. Connect backend for live data."],
        "stock_price":0.0,"stock_change":"N/A","stock_change_val":0,
        "market_cap":"N/A","pe_ratio":"N/A","week_high":"N/A","week_low":"N/A",
        "report_text":f"Mock analysis for {company}. Connect the FastAPI backend for real AI-generated data."
    })

def fetch_data(company):
    try:
        r = requests.get("http://localhost:8000/analyze", params={"company":company}, timeout=5)
        if r.status_code == 200:
            return r.json(), False
    except Exception:
        pass
    return get_mock(company), True

def check_keywords(data, keywords):
    text = " ".join(data["news_headlines"]).lower() + " " + data["report_text"].lower()
    return [kw for kw in keywords if kw.lower() in text]

def generate_pdf(data):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=50)
    S = getSampleStyleSheet()
    t = ParagraphStyle("T", fontSize=22, textColor=rl_colors.HexColor("#0F1923"), fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)
    s = ParagraphStyle("S", fontSize=11, textColor=rl_colors.HexColor("#555"), fontName="Helvetica", alignment=TA_CENTER, spaceAfter=20)
    h = ParagraphStyle("H", fontSize=13, textColor=rl_colors.HexColor("#0055AA"), fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6)
    b = ParagraphStyle("B", fontSize=10, textColor=rl_colors.HexColor("#222"), fontName="Helvetica", leading=16, spaceAfter=5)
    story = [
        Paragraph(f"Research Report: {data['company']}", t),
        Paragraph(f"Ticker: {data.get('ticker','N/A')}  |  Generated by FinResearch AI", s),
        Spacer(1,8), Paragraph("Sentiment Analysis", h),
        Paragraph(f"Score: <b>{data['sentiment_score']}</b>  |  Label: <b>{data['sentiment_label']}</b>  |  Positive: <b>{data['positive_pct']}%</b>  Negative: <b>{data['negative_pct']}%</b>", b),
        Spacer(1,6), Paragraph("Market Data", h),
        Paragraph(f"Stock Price: <b>${data['stock_price']}</b>  |  Change: <b>{data['stock_change']}</b>  |  Market Cap: <b>${data['market_cap']}</b>  |  P/E: <b>{data['pe_ratio']}</b>", b),
        Spacer(1,6), Paragraph("Recent News Headlines", h),
    ]
    for i, headline in enumerate(data["news_headlines"], 1):
        story.append(Paragraph(f"{i}. {headline}", b))
    story += [Spacer(1,6), Paragraph("AI-Generated Analysis", h), Paragraph(data["report_text"], b)]
    doc.build(story)
    buf.seek(0)
    return buf

# ══════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📊 FinResearch AI")
    st.markdown("<p style='color:#5A90B8;font-size:.82rem;margin-top:-8px'>Multi-Agent Financial Research</p>", unsafe_allow_html=True)
    st.divider()

    st.markdown("**Analysis Mode**")
    mode = st.radio("", ["Single Company", "Compare Companies"], label_visibility="collapsed")
    st.divider()

    st.markdown("**🔔 Keyword Alerts**")
    st.caption("System flags these words if found in news:")
    keywords_input = st.text_input("", "fraud, layoffs, lawsuit, bankruptcy, SEC", label_visibility="collapsed")
    st.divider()

    st.markdown("**🤖 How the agents work**")
    for i, step in enumerate(["Agent 1 — Fetch news (NewsAPI)", "Agent 2 — Score sentiment (LLM)", "Agent 3 — Get market data (yfinance)", "Agent 4 — Write report (LLM)"], 1):
        st.markdown(f"<div style='display:flex;align-items:center;gap:8px;padding:5px 0'><div style='width:20px;height:20px;border-radius:50%;background:#0077CC;color:#fff;font-size:.7rem;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0'>{i}</div><span style='font-size:.82rem;color:#7ABCDD'>{step}</span></div>", unsafe_allow_html=True)
    st.divider()
    st.caption("Built with LangGraph · FastAPI · Streamlit")
    st.caption("Educational use only — not financial advice")

keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]

# ══════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════
st.markdown("# 📊 Financial Research Assistant")
st.markdown("<p style='color:#5A90B8;font-size:.92rem;margin-top:-8px;margin-bottom:1rem'>Powered by 4 AI Agents — Live News · Sentiment Analysis · Market Data · Auto Reports</p>", unsafe_allow_html=True)
st.divider()

# ══════════════════════════════════════════════════════════
# SINGLE COMPANY
# ══════════════════════════════════════════════════════════
if mode == "Single Company":

    # ── Onboarding banner ────────────────────────────────
    if "data" not in st.session_state:
        st.markdown("""
        <div class="onboard-banner">
          <div class="onboard-title">👋 Welcome! Here's how to get started:</div>
          <div class="onboard-body">Type any company name in the box below and click <b style='color:#40C4FF'>Analyze →</b>. The 4 AI agents will automatically fetch news, score sentiment, pull stock data, and write a full report for you.</div>
          <div class="steps-row">
            <div class="step-pill"><div class="step-num">1</div> Type a company name</div>
            <div class="step-pill"><div class="step-num">2</div> Click Analyze →</div>
            <div class="step-pill"><div class="step-num">3</div> Read the results</div>
            <div class="step-pill"><div class="step-num">4</div> Download PDF report</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Search row ───────────────────────────────────────
    col_in, col_btn = st.columns([4, 1])
    with col_in:
        company = st.text_input("", placeholder="🔍  Type company name here — e.g. Apple, Tesla, Google, Microsoft...", label_visibility="collapsed")
    with col_btn:
        run = st.button("Analyze →", type="primary")

    st.caption("💡 Try: Apple · Microsoft · Tesla · Google · Amazon")

    if run and company.strip():
        with st.spinner(f"🤖 All 4 agents are analyzing {company}..."):
            time.sleep(0.8)
            data, is_mock = fetch_data(company)
        st.session_state["data"]    = data
        st.session_state["is_mock"] = is_mock
    elif run and not company.strip():
        st.markdown('<div class="alert-warn">⚠️ Please type a company name first, then click Analyze →</div>', unsafe_allow_html=True)

    data    = st.session_state.get("data", None)
    is_mock = st.session_state.get("is_mock", True)

    if data is None:
        st.stop()

    # ── Status banners ───────────────────────────────────
    if is_mock:
        st.markdown('<div class="alert-warn">⚠️ <b>Mock data mode</b> — backend not connected yet. Results are sample data. Once your teammate connects the FastAPI backend, this switches to live data automatically.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-ok">✅ Live data — connected to backend successfully.</div>', unsafe_allow_html=True)

    triggered = check_keywords(data, keywords)
    if triggered:
        st.markdown(f'<div class="alert-danger">🚨 <b>Risk Alert:</b> These keywords were found in recent news — <b>{", ".join(triggered)}</b></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-ok">✅ No risk keywords detected in recent news</div>', unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["🔍  Analysis", "📈  Sentiment Deep Dive", "📄  Full Report & PDF"])

    # TAB 1 — ANALYSIS
    with tab1:
        st.markdown(f'<div style="margin:.4rem 0 1rem"><span class="company-badge">📊 {data["company"]} &nbsp;·&nbsp; {data.get("ticker","")}</span></div>', unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Sentiment Score",  f"{data['sentiment_score']:.2f}", data["sentiment_label"])
        c2.metric("Stock Price",       f"${data['stock_price']}",       data["stock_change"])
        c3.metric("Market Cap",        f"${data['market_cap']}")
        c4.metric("P/E Ratio",         str(data["pe_ratio"]))

        st.markdown('<div class="sec-label">Recent News Headlines</div>', unsafe_allow_html=True)
        for h in data["news_headlines"]:
            st.markdown(f'<div class="news-item"><div class="news-dot"></div><span>{h}</span></div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-label" style="margin-top:1rem">AI-Generated Analysis</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="fin-card"><p style="color:#C8E0F4;line-height:1.85;font-size:.92rem">{data["report_text"]}</p></div>', unsafe_allow_html=True)

    # TAB 2 — SENTIMENT DEEP DIVE
    with tab2:
        st.markdown('<div class="sec-label">Sentiment Score Breakdown</div>', unsafe_allow_html=True)
        col_bars, col_nums = st.columns([3, 1])
        with col_bars:
            st.markdown(f"<p style='color:#00E676;font-weight:700;margin-bottom:4px'>Positive — {data['positive_pct']}%</p>", unsafe_allow_html=True)
            st.progress(data["positive_pct"] / 100)
            st.markdown(f"<p style='color:#7ABCDD;font-weight:700;margin-bottom:4px'>Neutral — {data['neutral_pct']}%</p>", unsafe_allow_html=True)
            st.progress(data["neutral_pct"] / 100)
            st.markdown(f"<p style='color:#FF5252;font-weight:700;margin-bottom:4px'>Negative — {data['negative_pct']}%</p>", unsafe_allow_html=True)
            st.progress(data["negative_pct"] / 100)
        with col_nums:
            st.metric("Positive", f"{data['positive_pct']}%")
            st.metric("Neutral",  f"{data['neutral_pct']}%")
            st.metric("Negative", f"{data['negative_pct']}%")

        st.markdown('<div class="sec-label" style="margin-top:1.2rem">Keyword Watch Status</div>', unsafe_allow_html=True)
        st.markdown("<p style='color:#7ABCDD;font-size:.85rem;margin-bottom:8px'>Each keyword is checked against all fetched news articles. Green = not found. Red = found in news.</p>", unsafe_allow_html=True)
        all_text = " ".join(data["news_headlines"]).lower() + " " + data["report_text"].lower()
        chip_html = ""
        for kw in keywords:
            if kw.lower() in all_text:
                chip_html += f'<span class="chip-bad">⚠ {kw}</span>'
            else:
                chip_html += f'<span class="chip-ok">✓ {kw}</span>'
        st.markdown(chip_html, unsafe_allow_html=True)

        st.markdown('<div class="sec-label" style="margin-top:1.2rem">52-Week Price Range</div>', unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        r1.metric("52-Week High", f"${data['week_high']}")
        r2.metric("52-Week Low",  f"${data['week_low']}")

    # TAB 3 — REPORT & PDF
    with tab3:
        st.markdown('<div class="sec-label">Full Report Preview</div>', unsafe_allow_html=True)
        with st.expander("📋 Click to expand full report", expanded=True):
            st.markdown(f"### {data['company']} — Research Report")
            st.divider()
            col_r1, col_r2 = st.columns(2)
            col_r1.markdown(f"**Sentiment:** {data['sentiment_label']} ({data['sentiment_score']:.2f})")
            col_r1.markdown(f"**Stock Price:** ${data['stock_price']}  {data['stock_change']}")
            col_r2.markdown(f"**Market Cap:** ${data['market_cap']}")
            col_r2.markdown(f"**P/E Ratio:** {data['pe_ratio']}")
            st.divider()
            st.markdown("**Recent Headlines:**")
            for h in data["news_headlines"]:
                st.markdown(f"- {h}")
            st.divider()
            st.markdown("**AI Analysis:**")
            st.markdown(f"<p style='color:#C8E0F4;line-height:1.85'>{data['report_text']}</p>", unsafe_allow_html=True)

        st.markdown('<div class="sec-label" style="margin-top:1rem">Export</div>', unsafe_allow_html=True)
        st.markdown("<p style='color:#7ABCDD;font-size:.85rem;margin-bottom:10px'>Download a professionally formatted PDF report to share or save.</p>", unsafe_allow_html=True)
        pdf = generate_pdf(data)
        st.download_button("📥 Download PDF Report", data=pdf,
                           file_name=f"{data['company']}_research_report.pdf", mime="application/pdf")

# ══════════════════════════════════════════════════════════
# COMPARE MODE
# ══════════════════════════════════════════════════════════
else:
    st.markdown("""
    <div class="onboard-banner">
      <div class="onboard-title">📊 Compare Multiple Companies Side by Side</div>
      <div class="onboard-body">Enter 2–3 company names separated by commas below. Click <b style='color:#40C4FF'>Compare All →</b> to run the full AI analysis for each company and see them side by side.</div>
    </div>
    """, unsafe_allow_html=True)

    col_ci, col_cb = st.columns([4, 1])
    with col_ci:
        companies_input = st.text_input("", "Apple, Microsoft, Tesla",
                                         placeholder="Enter companies — e.g. Apple, Microsoft, Tesla",
                                         label_visibility="collapsed")
    with col_cb:
        run_compare = st.button("Compare All →", type="primary")

    if run_compare:
        companies = [c.strip() for c in companies_input.split(",") if c.strip()]
        if len(companies) < 2:
            st.markdown('<div class="alert-warn">⚠️ Please enter at least 2 company names separated by commas.</div>', unsafe_allow_html=True)
        else:
            results, any_mock = {}, False
            with st.spinner("🤖 Analyzing all companies across all agents..."):
                for co in companies:
                    d, mock = fetch_data(co)
                    results[co] = d
                    if mock: any_mock = True
                time.sleep(0.6)
            st.session_state["compare_results"] = results
            st.session_state["compare_mock"]    = any_mock

    results  = st.session_state.get("compare_results", {})
    any_mock = st.session_state.get("compare_mock", False)

    if results:
        if any_mock:
            st.markdown('<div class="alert-warn">⚠️ Mock data mode — backend not connected yet.</div>', unsafe_allow_html=True)

        companies = list(results.keys())

        st.markdown('<div class="sec-label">Side-by-Side Metrics</div>', unsafe_allow_html=True)
        cols = st.columns(len(companies))
        for i, co in enumerate(companies):
            d = results[co]
            with cols[i]:
                st.markdown(f'<div style="text-align:center;margin-bottom:8px"><span class="company-badge">{d["company"]}</span></div>', unsafe_allow_html=True)
                st.metric("Sentiment",   f"{d['sentiment_score']:.2f}", d["sentiment_label"])
                st.metric("Stock Price", f"${d['stock_price']}",         d["stock_change"])
                st.metric("Market Cap",  f"${d['market_cap']}")
                st.metric("P/E Ratio",   str(d["pe_ratio"]))

        st.markdown('<div class="sec-label" style="margin-top:1rem">Latest Headlines</div>', unsafe_allow_html=True)
        cols2 = st.columns(len(companies))
        for i, co in enumerate(companies):
            with cols2[i]:
                st.markdown(f"<p style='color:#40C4FF;font-weight:700;margin-bottom:6px'>{co}</p>", unsafe_allow_html=True)
                for h in results[co]["news_headlines"][:3]:
                    st.markdown(f'<div class="news-item"><div class="news-dot"></div><span>{h}</span></div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-label" style="margin-top:1rem">AI Comparative Summary</div>', unsafe_allow_html=True)
        best  = max(results, key=lambda c: results[c]["sentiment_score"])
        worst = min(results, key=lambda c: results[c]["sentiment_score"])
        st.markdown(
            f'<div class="fin-card"><p style="color:#C8E0F4;line-height:1.85">'
            f'Based on current sentiment analysis, <b style="color:#00E676">{best}</b> shows the strongest positive outlook '
            f'(score: {results[best]["sentiment_score"]:.2f}). <b style="color:#FFD740">{worst}</b> has the lowest score '
            f'({results[worst]["sentiment_score"]:.2f}). This is an AI-generated summary only — always combine with deeper '
            f'fundamental analysis before making investment decisions.</p></div>',
            unsafe_allow_html=True)

        st.markdown('<div class="sec-label" style="margin-top:1rem">Keyword Alert Check — All Companies</div>', unsafe_allow_html=True)
        for co in companies:
            t = check_keywords(results[co], keywords)
            if t:
                st.markdown(f'<div class="alert-danger">🚨 <b>{co}:</b> Risk keywords found — {", ".join(t)}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-ok">✅ <b>{co}:</b> No risk keywords detected</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown('<p style="text-align:center;color:#1E4060;font-size:.78rem">FinResearch AI · Multi-Agent Financial Research · LangGraph + FastAPI + Streamlit · Educational use only — not financial advice</p>', unsafe_allow_html=True)