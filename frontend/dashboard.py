import streamlit as st
import requests
import io
import time
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors as rl_colors

st.set_page_config(page_title="FinResearch AI", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
#MainMenu,footer,header{visibility:hidden}
.stApp{background:#0D1520}
.main .block-container{padding:1.5rem 2rem;max-width:1200px}
[data-testid="stSidebar"]{background:#0A1120!important;border-right:1px solid #1A2D40}
[data-testid="stSidebar"] *{color:#C8E0F4!important}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3{color:#FFFFFF!important}
[data-testid="metric-container"]{background:#0F1F32;border:1px solid #1A3050;border-radius:12px;padding:14px 16px}
[data-testid="metric-container"] label{color:#4A90B8!important;font-size:.72rem!important;text-transform:uppercase;letter-spacing:.06em}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#FFFFFF!important;font-size:1.8rem!important;font-weight:700!important}
[data-testid="metric-container"] [data-testid="stMetricDelta"]{font-size:.8rem!important}
.stButton>button{background:#0077CC;color:#FFFFFF;border:none;border-radius:8px;padding:.55rem 1.6rem;font-weight:700;font-size:.95rem;width:100%}
.stButton>button:hover{background:#0088EE;box-shadow:0 0 0 3px rgba(0,120,200,.25)}
.stDownloadButton>button{background:#0F2A44!important;color:#40C4FF!important;border:1px solid #0077CC!important;border-radius:8px!important;width:100%;font-weight:700!important}
.stDownloadButton>button:hover{background:#1A3A55!important}
.stTextInput>div>div>input{background:#0F1F32!important;border:1px solid #1A3050!important;border-radius:8px!important;color:#FFFFFF!important;font-size:.95rem!important}
.stTextInput>div>div>input:focus{border-color:#0077CC!important;box-shadow:0 0 0 3px rgba(0,119,204,.2)!important}
.stTextInput>div>div>input::placeholder{color:#3A6080!important}
.stTabs [data-baseweb="tab-list"]{background:#0A1628;border-radius:10px;padding:4px;gap:4px;border:1px solid #1A3050}
.stTabs [data-baseweb="tab"]{background:transparent;color:#5A90B8;border-radius:8px;padding:7px 22px;font-size:.88rem;font-weight:500}
.stTabs [aria-selected="true"]{background:#0077CC!important;color:#FFFFFF!important;font-weight:700!important}
.stTabs [data-baseweb="tab-border"]{display:none}
.stTabs [data-baseweb="tab-panel"]{padding-top:1.2rem}
.streamlit-expanderHeader{background:#0F1F32!important;border:1px solid #1A3050!important;border-radius:8px!important;color:#FFFFFF!important;font-weight:600!important}
.streamlit-expanderContent{background:#080F1A!important;border:1px solid #1A3050!important;border-top:none!important}
.stProgress>div>div{background:#0A1628!important}
.stProgress>div>div>div{background:linear-gradient(90deg,#0077CC,#00C4FF)!important;border-radius:99px!important}
.stRadio label{color:#C8E0F4!important;font-size:.9rem!important}
p,li,span,div{color:#C8E0F4}
h1,h2,h3{color:#FFFFFF!important}
hr{border-color:#1A2D40!important}
.stMarkdown p{color:#C8E0F4;line-height:1.75}
label{color:#7ABCDD!important}
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
.agent-step{display:flex;align-items:center;gap:10px;padding:10px 14px;background:#080F1A;border:1px solid #122030;border-radius:8px;margin-bottom:6px}
.agent-num{width:26px;height:26px;border-radius:50%;background:#0077CC;color:#fff;font-size:.8rem;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.agent-name{font-size:.9rem;font-weight:700;color:#FFFFFF}
.agent-desc{font-size:.78rem;color:#5A90B8;margin-top:1px}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# MOCK DATA — fallback when backend is offline
# ══════════════════════════════════════════════════════════
MOCK = {
    "apple": {
        "company":"Apple","ticker":"AAPL",
        "sentiment_score":0.72,"sentiment_label":"Positive",
        "positive_pct":72,"neutral_pct":21,"negative_pct":7,
        "news_headlines":["Apple hits record quarterly revenue of $120B",
                          "iPhone 16 sales surpass analyst expectations",
                          "Apple expands AI features across product lineup",
                          "Apple stock reaches all-time high amid strong earnings",
                          "New MacBook with M4 chip receives rave reviews"],
        "stock_price":189.50,"stock_change":"+1.2%",
        "market_cap":"2.94T","pe_ratio":28.5,
        "week_high":198.23,"week_low":142.10,
        "recommendation":"Buy","analyst_target":210.0,
        "articles_analyzed":47,
        "report_text":"Apple Inc. demonstrated strong positive momentum this week, driven by better-than-expected quarterly earnings and continued growth in its services segment. Sentiment across financial media remained largely bullish, with analysts highlighting the company's expanding AI integration as a key growth driver. Stock performance has been resilient, trading near all-time highs. Overall outlook remains positive with no significant risk flags detected."
    },
    "microsoft": {
        "company":"Microsoft","ticker":"MSFT",
        "sentiment_score":0.65,"sentiment_label":"Positive",
        "positive_pct":65,"neutral_pct":28,"negative_pct":7,
        "news_headlines":["Microsoft Azure cloud revenue grows 28% year over year",
                          "Copilot AI adoption accelerating across enterprise clients",
                          "Microsoft acquires gaming studio for $1.2B",
                          "Teams reaches 320 million daily active users",
                          "Microsoft beats earnings estimates for third straight quarter"],
        "stock_price":415.20,"stock_change":"+0.8%",
        "market_cap":"3.08T","pe_ratio":35.2,
        "week_high":430.82,"week_low":310.50,
        "recommendation":"Buy","analyst_target":450.0,
        "articles_analyzed":42,
        "report_text":"Microsoft Corp. continues to show strong fundamentals, led by cloud and AI-driven growth. Azure's accelerating revenue growth and Copilot adoption signal a strong enterprise AI transition. Sentiment is broadly positive, though some analysts note valuation concerns at current price levels. No major risk flags detected."
    },
    "tesla": {
        "company":"Tesla","ticker":"TSLA",
        "sentiment_score":0.28,"sentiment_label":"Neutral",
        "positive_pct":38,"neutral_pct":24,"negative_pct":38,
        "news_headlines":["Tesla misses delivery estimates for second consecutive quarter",
                          "Elon Musk announces new affordable EV model for 2025",
                          "Tesla faces increased competition from Chinese EV manufacturers",
                          "Autopilot investigation continues amid safety concerns",
                          "Tesla energy storage division posts record revenue"],
        "stock_price":245.30,"stock_change":"-2.1%",
        "market_cap":"0.78T","pe_ratio":52.8,
        "week_high":298.43,"week_low":138.80,
        "recommendation":"Hold","analyst_target":260.0,
        "articles_analyzed":50,
        "report_text":"Tesla Inc. presents a mixed picture this week. While the energy storage division continues to perform well, vehicle delivery shortfalls and increasing competition from Chinese EV manufacturers have weighed on sentiment. Regulatory scrutiny around Autopilot adds further uncertainty. Investors should monitor delivery figures closely."
    },
}

def get_mock(company):
    return MOCK.get(company.lower().strip(), {
        "company":company,"ticker":"N/A",
        "sentiment_score":0.5,"sentiment_label":"Neutral",
        "positive_pct":50,"neutral_pct":35,"negative_pct":15,
        "news_headlines":[f"No mock data for {company}. Connect backend for live data."],
        "stock_price":0.0,"stock_change":"N/A",
        "market_cap":"N/A","pe_ratio":"N/A",
        "week_high":"N/A","week_low":"N/A",
        "recommendation":"N/A","analyst_target":0.0,
        "articles_analyzed":0,
        "report_text":f"Mock analysis for {company}. Start the FastAPI backend and try again."
    })

# ══════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════
def _calc_pct(scores, mode):
    if not scores: return {"positive":50,"neutral":35,"negative":15}[mode]
    total = len(scores)
    if mode == "positive":
        return round(len([s for s in scores if s.get("score",0) >  0.2]) / total * 100)
    if mode == "negative":
        return round(len([s for s in scores if s.get("score",0) < -0.2]) / total * 100)
    pos = _calc_pct(scores,"positive")
    neg = _calc_pct(scores,"negative")
    return max(0, 100 - pos - neg)

def _fmt_market_cap(val):
    """Format market cap from raw number to readable string."""
    if val is None: return "N/A"
    if isinstance(val, str): return val
    if val >= 1_000_000_000_000:
        return f"{val/1_000_000_000_000:.2f}T"
    if val >= 1_000_000_000:
        return f"{val/1_000_000_000:.2f}B"
    return str(val)

def _fmt_price(val):
    if val is None: return "N/A"
    if isinstance(val, (int, float)): return round(val, 2)
    return val

def translate_response(raw, company):
    """Translate backend API response to dashboard format."""
    scores     = raw.get("sentiment_scores", [])
    market     = raw.get("market_data", {}) if "market_data" in raw else raw
    price      = raw.get("current_price") or market.get("current_price")
    prev_close = raw.get("previous_close") or market.get("previous_close")

    # Calculate stock change
    if price and prev_close:
        change_val = ((price - prev_close) / prev_close) * 100
        stock_change = f"{'+' if change_val >= 0 else ''}{change_val:.1f}%"
    else:
        stock_change = "N/A"

    return {
        "company":          raw.get("company", company),
        "ticker":           raw.get("ticker", ""),
        "sentiment_score":  raw.get("overall_sentiment", 0.5),
        "sentiment_label":  raw.get("sentiment_label", "Neutral"),
        "positive_pct":     _calc_pct(scores, "positive"),
        "neutral_pct":      _calc_pct(scores, "neutral"),
        "negative_pct":     _calc_pct(scores, "negative"),
        "news_headlines":   raw.get("top_headlines", []),
        "stock_price":      _fmt_price(price),
        "stock_change":     stock_change,
        "market_cap":       _fmt_market_cap(raw.get("market_cap")),
        "pe_ratio":         _fmt_price(raw.get("pe_ratio")),
        "week_high":        _fmt_price(raw.get("week_52_high")),
        "week_low":         _fmt_price(raw.get("week_52_low")),
        "recommendation":   raw.get("recommendation", "N/A"),
        "analyst_target":   _fmt_price(raw.get("analyst_target")),
        "articles_analyzed":raw.get("articles_analyzed", 0),
        "report_text":      raw.get("report", ""),
    }

def fetch_data(company, ticker=""):
    """Call backend API. Falls back to mock data if backend is offline."""
    if not ticker:
        ticker = company[:4].upper()
    try:
        r = requests.post(
            "http://localhost:8000/analyze",
            json={"company": company, "ticker": ticker, "use_cache": True},
            timeout=60,  # pipeline takes ~30 seconds
        )
        if r.status_code == 200:
            return translate_response(r.json(), company), False
    except Exception as e:
        print(f"[Dashboard] Backend error: {e}")
    return get_mock(company), True

def check_keywords(data, keywords):
    text = " ".join(data.get("news_headlines",[])).lower() + " " + data.get("report_text","").lower()
    return [kw for kw in keywords if kw.lower() in text]

def generate_pdf(data):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=50)
    t = ParagraphStyle("T", fontSize=22, textColor=rl_colors.HexColor("#0F1923"), fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)
    s = ParagraphStyle("S", fontSize=11, textColor=rl_colors.HexColor("#555"), fontName="Helvetica", alignment=TA_CENTER, spaceAfter=20)
    h = ParagraphStyle("H", fontSize=13, textColor=rl_colors.HexColor("#0055AA"), fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6)
    b = ParagraphStyle("B", fontSize=10, textColor=rl_colors.HexColor("#222"), fontName="Helvetica", leading=16, spaceAfter=5)
    story = [
        Paragraph(f"Research Report: {data['company']}", t),
        Paragraph(f"Ticker: {data.get('ticker','N/A')}  |  Articles Analyzed: {data.get('articles_analyzed',0)}  |  FinResearch AI", s),
        Spacer(1,8),
        Paragraph("Sentiment Analysis", h),
        Paragraph(f"Score: <b>{data['sentiment_score']:.2f}</b>  |  Label: <b>{data['sentiment_label']}</b>  |  Positive: <b>{data['positive_pct']}%</b>  Neutral: <b>{data['neutral_pct']}%</b>  Negative: <b>{data['negative_pct']}%</b>", b),
        Spacer(1,6),
        Paragraph("Market Data", h),
        Paragraph(f"Price: <b>${data['stock_price']}</b>  |  Change: <b>{data['stock_change']}</b>  |  Market Cap: <b>${data['market_cap']}</b>  |  P/E: <b>{data['pe_ratio']}</b>  |  52W High: <b>${data['week_high']}</b>  |  52W Low: <b>${data['week_low']}</b>", b),
        Paragraph(f"Analyst Recommendation: <b>{data.get('recommendation','N/A')}</b>  |  Target Price: <b>${data.get('analyst_target','N/A')}</b>", b),
        Spacer(1,6),
        Paragraph("Recent News Headlines", h),
    ]
    for i, headline in enumerate(data.get("news_headlines",[]), 1):
        story.append(Paragraph(f"{i}. {headline}", b))
    story += [Spacer(1,6), Paragraph("AI-Generated Analysis", h), Paragraph(data.get("report_text",""), b)]
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
    mode = st.radio("mode", ["Single Company", "Compare Companies"], label_visibility="collapsed")
    st.divider()
    st.markdown("**🔔 Keyword Alerts**")
    st.caption("Flags these words if found in news:")
    keywords_input = st.text_input("keywords", "fraud, layoffs, lawsuit, bankruptcy, SEC", label_visibility="collapsed")
    st.divider()
    st.markdown("**🤖 Agent Pipeline**")
    for i, (name, desc) in enumerate([
        ("News Fetcher",       "NewsAPI — fetches 50 articles"),
        ("Sentiment Analyzer", "LLM — scores each article"),
        ("Market Data",        "yfinance — live stock data"),
        ("Report Writer",      "LLM — writes full report"),
    ], 1):
        st.markdown(f"""
        <div class="agent-step">
          <div class="agent-num">{i}</div>
          <div><div class="agent-name">{name}</div><div class="agent-desc">{desc}</div></div>
        </div>""", unsafe_allow_html=True)
    st.divider()
    st.caption("LangGraph · FastAPI · Streamlit")

keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]

# ══════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════
st.markdown("# 📊 Financial Research Assistant")
st.markdown("<p style='color:#5A90B8;font-size:.92rem;margin-top:-8px;margin-bottom:1rem'>Powered by 4 AI Agents — Live News · Sentiment Analysis · Market Data · Auto Reports</p>", unsafe_allow_html=True)
st.divider()

# ══════════════════════════════════════════════════════════
# SINGLE COMPANY MODE
# ══════════════════════════════════════════════════════════
if mode == "Single Company":

    if "data" not in st.session_state:
        st.markdown("""
        <div class="onboard-banner">
          <div class="onboard-title">👋 Welcome! Here's how to get started:</div>
          <div class="onboard-body">Type any company name + ticker below and click <b style='color:#40C4FF'>Analyze →</b>. All 4 AI agents will run automatically and generate a full research report.</div>
          <div class="steps-row">
            <div class="step-pill"><div class="step-num">1</div>Type company + ticker</div>
            <div class="step-pill"><div class="step-num">2</div>Click Analyze →</div>
            <div class="step-pill"><div class="step-num">3</div>Read the report</div>
            <div class="step-pill"><div class="step-num">4</div>Download PDF</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Input row ────────────────────────────────────────
    c1, c2, c3 = st.columns([3, 1.2, 1])
    with c1:
        company = st.text_input("Company Name", placeholder="Company name — Apple, Tesla, Microsoft...", label_visibility="collapsed")
    with c2:
        ticker = st.text_input("Ticker Symbol", placeholder="Ticker — AAPL, TSLA...", label_visibility="collapsed")
    with c3:
        run = st.button("Analyze →", type="primary")

    st.caption("💡 Try: Apple / AAPL · Microsoft / MSFT · Tesla / TSLA · Google / GOOGL · Amazon / AMZN")

    if run and company.strip():
        # ── Agent progress animation ──────────────────
        progress_bar = st.progress(0)
        status       = st.empty()
        steps = [
            (25,  "🔵 Agent 1 — Fetching latest news articles..."),
            (50,  "🟡 Agent 2 — Analyzing sentiment across articles..."),
            (75,  "🟢 Agent 3 — Retrieving live market data..."),
            (95,  "🔴 Agent 4 — Writing analyst report..."),
        ]
        for pct, msg in steps:
            status.markdown(f"<p style='color:#7ABCDD;font-size:.88rem'>{msg}</p>", unsafe_allow_html=True)
            progress_bar.progress(pct)
            time.sleep(0.4)

        data, is_mock = fetch_data(company.strip(), ticker.strip())

        progress_bar.progress(100)
        status.markdown("<p style='color:#00E676;font-size:.88rem'>✅ Analysis complete!</p>", unsafe_allow_html=True)
        time.sleep(0.5)
        progress_bar.empty()
        status.empty()

        st.session_state["data"]    = data
        st.session_state["is_mock"] = is_mock

    elif run and not company.strip():
        st.markdown('<div class="alert-warn">⚠️ Please type a company name first.</div>', unsafe_allow_html=True)

    data    = st.session_state.get("data", None)
    is_mock = st.session_state.get("is_mock", True)

    if data is None:
        st.markdown('<div class="alert-warn" style="margin-top:1rem">👆 Enter a company name above and click Analyze to get started.</div>', unsafe_allow_html=True)
        st.stop()

    # ── Status banners ───────────────────────────────
    if is_mock:
        st.markdown('<div class="alert-warn">⚠️ <b>Mock data</b> — backend not reachable. Start the FastAPI server and try again for live results.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="alert-ok">✅ Live data — {data.get("articles_analyzed", 0)} articles analyzed by AI agents.</div>', unsafe_allow_html=True)

    triggered = check_keywords(data, keywords)
    if triggered:
        st.markdown(f'<div class="alert-danger">🚨 <b>Risk keywords detected:</b> {", ".join(triggered)}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-ok">✅ No risk keywords found in recent news</div>', unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Analysis", "📈 Sentiment", "💹 Market Data", "📄 Report & PDF"])

    # TAB 1 — ANALYSIS
    with tab1:
        st.markdown(f'<div style="margin:.4rem 0 1rem"><span class="company-badge">📊 {data["company"]} &nbsp;·&nbsp; {data.get("ticker","")}</span></div>', unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Sentiment Score",  f"{data['sentiment_score']:.2f}", data["sentiment_label"])
        c2.metric("Stock Price",       f"${data['stock_price']}",        data["stock_change"])
        c3.metric("Market Cap",        f"${data['market_cap']}")
        c4.metric("Articles Analyzed", str(data.get("articles_analyzed", 0)))

        st.markdown('<div class="sec-label">Recent News Headlines</div>', unsafe_allow_html=True)
        for h in data.get("news_headlines", []):
            st.markdown(f'<div class="news-item"><div class="news-dot"></div><span>{h}</span></div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-label" style="margin-top:1rem">AI Analysis Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="fin-card"><p style="color:#C8E0F4;line-height:1.85;font-size:.92rem">{data["report_text"][:400]}{"..." if len(data["report_text"]) > 400 else ""}</p></div>', unsafe_allow_html=True)
        st.caption("Full report available in the Report & PDF tab →")

    # TAB 2 — SENTIMENT
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

        st.markdown('<div class="sec-label" style="margin-top:1.2rem">Keyword Watch</div>', unsafe_allow_html=True)
        all_text = " ".join(data.get("news_headlines",[])).lower()
        chip_html = ""
        for kw in keywords:
            if kw.lower() in all_text:
                chip_html += f'<span class="chip-bad">⚠ {kw}</span>'
            else:
                chip_html += f'<span class="chip-ok">✓ {kw}</span>'
        st.markdown(chip_html, unsafe_allow_html=True)

    # TAB 3 — MARKET DATA
    with tab3:
        st.markdown(f'<div style="margin:.4rem 0 1rem"><span class="company-badge">💹 {data["company"]} &nbsp;·&nbsp; {data.get("ticker","")}</span></div>', unsafe_allow_html=True)

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Stock Price",   f"${data['stock_price']}", data["stock_change"])
        r2.metric("Market Cap",    f"${data['market_cap']}")
        r3.metric("P/E Ratio",     str(data["pe_ratio"]))
        r4.metric("Analyst Target",f"${data.get('analyst_target','N/A')}")

        st.markdown('<div class="sec-label" style="margin-top:1rem">52-Week Range</div>', unsafe_allow_html=True)
        w1, w2, w3 = st.columns(3)
        w1.metric("52W High",        f"${data['week_high']}")
        w2.metric("52W Low",         f"${data['week_low']}")
        w3.metric("Recommendation",  str(data.get("recommendation","N/A")))

    # TAB 4 — REPORT & PDF
    with tab4:
        st.markdown('<div class="sec-label">Full AI-Generated Report</div>', unsafe_allow_html=True)
        with st.expander("📋 Click to read full report", expanded=True):
            st.markdown(f"### {data['company']} Research Report")
            st.divider()
            col_r1, col_r2 = st.columns(2)
            col_r1.markdown(f"**Sentiment:** {data['sentiment_label']} ({data['sentiment_score']:.2f})")
            col_r1.markdown(f"**Stock Price:** ${data['stock_price']}  {data['stock_change']}")
            col_r1.markdown(f"**Recommendation:** {data.get('recommendation','N/A')}")
            col_r2.markdown(f"**Market Cap:** ${data['market_cap']}")
            col_r2.markdown(f"**P/E Ratio:** {data['pe_ratio']}")
            col_r2.markdown(f"**Analyst Target:** ${data.get('analyst_target','N/A')}")
            st.divider()
            st.markdown("**Headlines Analyzed:**")
            for h in data.get("news_headlines", []):
                st.markdown(f"- {h}")
            st.divider()
            st.markdown("**Full Analysis:**")
            st.markdown(f"<p style='color:#C8E0F4;line-height:1.85'>{data['report_text']}</p>", unsafe_allow_html=True)

        st.markdown('<div class="sec-label" style="margin-top:1rem">Download</div>', unsafe_allow_html=True)
        st.markdown("<p style='color:#7ABCDD;font-size:.85rem;margin-bottom:10px'>Export this report as a PDF to share or save.</p>", unsafe_allow_html=True)
        pdf = generate_pdf(data)
        st.download_button("📥 Download PDF Report", data=pdf,
                           file_name=f"{data['company']}_research_report.pdf",
                           mime="application/pdf")

# ══════════════════════════════════════════════════════════
# COMPARE MODE
# ══════════════════════════════════════════════════════════
else:
    st.markdown("""
    <div class="onboard-banner">
      <div class="onboard-title">📊 Compare Multiple Companies</div>
      <div class="onboard-body">Enter 2–3 companies with their tickers below and click <b style='color:#40C4FF'>Compare All →</b> to run the full AI analysis for each.</div>
    </div>
    """, unsafe_allow_html=True)

    ci, cb = st.columns([4, 1])
    with ci:
        companies_input = st.text_input("Companies", "Apple|AAPL, Microsoft|MSFT, Tesla|TSLA",
                                         placeholder="Format: Apple|AAPL, Microsoft|MSFT",
                                         label_visibility="collapsed")
    with cb:
        run_compare = st.button("Compare All →", type="primary")

    st.caption("Format: CompanyName|TICKER — e.g. Apple|AAPL, Microsoft|MSFT")

    if run_compare:
        # Parse "Apple|AAPL, Microsoft|MSFT" format
        pairs = []
        for item in companies_input.split(","):
            item = item.strip()
            if "|" in item:
                parts = item.split("|")
                pairs.append((parts[0].strip(), parts[1].strip()))
            else:
                pairs.append((item, item[:4].upper()))

        if len(pairs) < 2:
            st.markdown('<div class="alert-warn">⚠️ Please enter at least 2 companies.</div>', unsafe_allow_html=True)
        else:
            results, any_mock = {}, False
            prog = st.progress(0)
            for i, (co, tk) in enumerate(pairs):
                st.markdown(f"<p style='color:#7ABCDD;font-size:.85rem'>Analyzing {co}...</p>", unsafe_allow_html=True)
                d, mock = fetch_data(co, tk)
                results[co] = d
                if mock: any_mock = True
                prog.progress(int((i+1)/len(pairs)*100))
            prog.empty()
            st.session_state["compare_results"] = results
            st.session_state["compare_mock"]    = any_mock

    results  = st.session_state.get("compare_results", {})
    any_mock = st.session_state.get("compare_mock", False)

    if results:
        if any_mock:
            st.markdown('<div class="alert-warn">⚠️ Mock data — backend not connected.</div>', unsafe_allow_html=True)

        companies = list(results.keys())

        st.markdown('<div class="sec-label">Side-by-Side Metrics</div>', unsafe_allow_html=True)
        cols = st.columns(len(companies))
        for i, co in enumerate(companies):
            d = results[co]
            with cols[i]:
                st.markdown(f'<div style="text-align:center;margin-bottom:8px"><span class="company-badge">{d["company"]}</span></div>', unsafe_allow_html=True)
                st.metric("Sentiment",    f"{d['sentiment_score']:.2f}", d["sentiment_label"])
                st.metric("Stock Price",  f"${d['stock_price']}",         d["stock_change"])
                st.metric("Market Cap",   f"${d['market_cap']}")
                st.metric("Recomm.",      str(d.get("recommendation","N/A")))

        st.markdown('<div class="sec-label" style="margin-top:1rem">Sentiment Comparison</div>', unsafe_allow_html=True)
        chart_data = {co: results[co]["sentiment_score"] for co in companies}
        st.bar_chart(chart_data)

        st.markdown('<div class="sec-label" style="margin-top:1rem">Latest Headlines</div>', unsafe_allow_html=True)
        cols2 = st.columns(len(companies))
        for i, co in enumerate(companies):
            with cols2[i]:
                st.markdown(f"<p style='color:#40C4FF;font-weight:700;margin-bottom:6px'>{co}</p>", unsafe_allow_html=True)
                for h in results[co].get("news_headlines",[])[:3]:
                    st.markdown(f'<div class="news-item"><div class="news-dot"></div><span>{h}</span></div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-label" style="margin-top:1rem">AI Comparative Summary</div>', unsafe_allow_html=True)
        best  = max(results, key=lambda c: results[c]["sentiment_score"])
        worst = min(results, key=lambda c: results[c]["sentiment_score"])
        st.markdown(
            f'<div class="fin-card"><p style="color:#C8E0F4;line-height:1.85">'
            f'Based on sentiment analysis across {len(companies)} companies, '
            f'<b style="color:#00E676">{best}</b> shows the strongest positive outlook '
            f'(score: {results[best]["sentiment_score"]:.2f}, recommendation: {results[best].get("recommendation","N/A")}). '
            f'<b style="color:#FFD740">{worst}</b> has the lowest sentiment score '
            f'({results[worst]["sentiment_score"]:.2f}). '
            f'AI-generated summary only — not financial advice.</p></div>',
            unsafe_allow_html=True)

        st.markdown('<div class="sec-label">Keyword Alerts</div>', unsafe_allow_html=True)
        for co in companies:
            t = check_keywords(results[co], keywords)
            if t:
                st.markdown(f'<div class="alert-danger">🚨 <b>{co}:</b> {", ".join(t)}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-ok">✅ <b>{co}:</b> No risk keywords detected</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown('<p style="text-align:center;color:#1E4060;font-size:.78rem">FinResearch AI · LangGraph + FastAPI + Streamlit · Built by Purvanshi & [Your Name] · BTech 3rd Year</p>', unsafe_allow_html=True)