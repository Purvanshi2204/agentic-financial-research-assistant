import streamlit as st
import requests
import yfinance as yf
import io
import time
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors as rl_colors

st.set_page_config(page_title="FinResearch AI", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
#MainMenu,footer,header{visibility:hidden}
.stApp{background:#0B0F19}
.main .block-container{padding:1.2rem 1.8rem;max-width:1200px}

[data-testid="stSidebar"]{background:#0E1420!important;border-right:1px solid #1C2840}
[data-testid="stSidebar"] *{color:#FFFFFF!important}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] span{color:#90AABF!important}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2{color:#FFFFFF!important}

[data-testid="metric-container"]{background:#0E1420;border:1px solid #1C2840;border-radius:12px;padding:14px 16px}
[data-testid="metric-container"] label{color:#3A6080!important;font-size:.68rem!important;text-transform:uppercase;letter-spacing:.08em;font-weight:700}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#FFFFFF!important;font-size:1.9rem!important;font-weight:800!important;line-height:1.1}
[data-testid="metric-container"] [data-testid="stMetricDelta"]{font-size:.78rem!important}

.stButton>button{background:#4EEAFF!important;color:#000000!important;border:none!important;border-radius:10px;padding:.6rem 1.8rem;font-weight:900!important;font-size:1.1rem!important;width:100%;letter-spacing:-.1px;text-shadow:none}
.stButton>button:hover{background:#7AF0FF!important}

.stDownloadButton>button{background:#34D399!important;color:#052510!important;border:none!important;border-radius:10px!important;width:100%;font-weight:800!important;font-size:1rem!important;padding:.7rem!important}
.stDownloadButton>button:hover{background:#6EE7B7!important}

.stTextInput>div>div>input{background:#131D2E!important;border:1.5px solid #1C2840!important;border-radius:10px!important;color:#FFFFFF!important;font-size:.95rem!important;padding:10px 14px!important}
.stTextInput>div>div>input:focus{border-color:#4EEAFF!important;box-shadow:0 0 0 3px rgba(78,234,255,.15)!important}
.stTextInput>div>div>input::placeholder{color:#2A5070!important}

.stTabs [data-baseweb="tab-list"]{background:#0E1420;border-radius:10px;padding:4px;gap:4px;border:1px solid #1C2840}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:#3A6080;border-radius:8px;padding:8px 20px;font-size:.88rem;font-weight:500}
.stTabs [aria-selected="true"]{background:#162030!important;color:#FFFFFF!important;font-weight:700!important}
.stTabs [data-baseweb="tab-border"]{display:none}
.stTabs [data-baseweb="tab-panel"]{padding-top:1.2rem}

.streamlit-expanderHeader{background:#0E1420!important;border:1px solid #1C2840!important;border-radius:8px!important;color:#FFFFFF!important;font-weight:700!important}
.streamlit-expanderContent{background:#080F1A!important;border:1px solid #1C2840!important;border-top:none!important}

.stProgress>div>div{background:#131D2E!important}
.stProgress>div>div>div{background:#4EEAFF!important;border-radius:99px!important}

.stRadio label{color:#C8E0F4!important;font-size:.9rem!important}

p,li,span,div{color:#C8E0F4}
h1,h2,h3{color:#FFFFFF!important}
hr{border-color:#1C2840!important}
.stMarkdown p{color:#C8E0F4;line-height:1.75}
label{color:#90AABF!important}

.status-bar{display:flex;align-items:center;gap:10px;padding:10px 16px;border-radius:0 8px 8px 0;font-size:.88rem;font-weight:500;margin:.25rem 0}
.status-live{background:#052510;border-left:3px solid #34D399;color:#34D399}
.status-mock{background:#180E00;border-left:3px solid #FB923C;color:#FB923C}
.status-risk{background:#130308;border-left:3px solid #F87171;color:#F87171}

.sec-label{font-size:.7rem;font-weight:700;color:#2A5070;text-transform:uppercase;letter-spacing:.1em;padding-bottom:8px;border-bottom:1px solid #131D2E;margin-bottom:12px}
.card-wrap{background:#0E1420;border:1px solid #1C2840;border-radius:12px;padding:16px 18px;margin-bottom:.6rem}
.news-item{display:flex;align-items:flex-start;gap:9px;padding:7px 0;border-bottom:1px solid #0D1628}
.news-dot{width:6px;height:6px;border-radius:50%;background:#4EEAFF;flex-shrink:0;margin-top:5px}
.news-text{font-size:.87rem;color:#C8E0F4;line-height:1.55}
.chip-ok{display:inline-block;background:#052510;border:1px solid #065F46;color:#34D399;border-radius:99px;padding:3px 11px;font-size:.75rem;margin:3px;font-weight:600}
.chip-bad{display:inline-block;background:#130308;border:1px solid #7F1D1D;color:#F87171;border-radius:99px;padding:3px 11px;font-size:.75rem;margin:3px;font-weight:600}
.company-title{font-size:1.15rem;font-weight:800;color:#FFFFFF;display:flex;align-items:center;gap:10px;margin-bottom:1rem}
.ticker-pill{background:#131D2E;border:1px solid #1C2840;color:#4EEAFF;border-radius:6px;padding:3px 12px;font-size:.82rem;font-family:monospace;font-weight:700}
.pdf-label{font-size:.95rem;font-weight:700;color:#FFFFFF;margin-bottom:6px}
.pdf-sub{font-size:.82rem;color:#3A6080;margin-bottom:12px}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# AUTO TICKER
# ══════════════════════════════════════════════════════════
TICKERS = {
    "apple":"AAPL","microsoft":"MSFT","tesla":"TSLA","google":"GOOGL",
    "alphabet":"GOOGL","amazon":"AMZN","meta":"META","facebook":"META",
    "netflix":"NFLX","nvidia":"NVDA","intel":"INTC","amd":"AMD",
    "samsung":"005930.KS","reliance":"RELIANCE.NS","tata":"TCS.NS",
    "infosys":"INFY","wipro":"WIPRO.NS","jpmorgan":"JPM","jp morgan":"JPM",
    "goldman":"GS","disney":"DIS","nike":"NKE","uber":"UBER",
    "airbnb":"ABNB","spotify":"SPOT","adobe":"ADBE","oracle":"ORCL","ibm":"IBM",
}

def get_ticker(company):
    key = company.lower().strip()
    if key in TICKERS:
        return TICKERS[key]
    try:
        r = yf.Search(company, max_results=1).quotes
        if r:
            return r[0].get("symbol", "")
    except:
        pass
    return ""

# ══════════════════════════════════════════════════════════
# MOCK DATA
# ══════════════════════════════════════════════════════════
MOCK = {
    "apple":{"company":"Apple","ticker":"AAPL","sentiment_score":0.72,"sentiment_label":"Positive","positive_pct":72,"neutral_pct":21,"negative_pct":7,"news_headlines":["Apple hits record quarterly revenue of $120B","iPhone 16 sales surpass analyst expectations","Apple expands AI features across product lineup","Apple stock reaches all-time high amid strong earnings","New MacBook with M4 chip receives rave reviews"],"stock_price":189.50,"stock_change":"+1.2%","market_cap":"2.94T","pe_ratio":28.5,"week_high":198.23,"week_low":142.10,"recommendation":"Buy","analyst_target":210.0,"articles_analyzed":47,"report_text":"Apple Inc. demonstrated strong positive momentum this week, driven by better-than-expected quarterly earnings and continued growth in its services segment. Sentiment across financial media remained largely bullish, with analysts highlighting the company's expanding AI integration as a key growth driver. Stock performance has been resilient, trading near all-time highs."},
    "microsoft":{"company":"Microsoft","ticker":"MSFT","sentiment_score":0.65,"sentiment_label":"Positive","positive_pct":65,"neutral_pct":28,"negative_pct":7,"news_headlines":["Microsoft Azure cloud revenue grows 28% year over year","Copilot AI adoption accelerating across enterprise clients","Microsoft acquires gaming studio for $1.2B","Teams reaches 320 million daily active users","Microsoft beats earnings estimates for third straight quarter"],"stock_price":415.20,"stock_change":"+0.8%","market_cap":"3.08T","pe_ratio":35.2,"week_high":430.82,"week_low":310.50,"recommendation":"Buy","analyst_target":450.0,"articles_analyzed":42,"report_text":"Microsoft Corp. continues to show strong fundamentals, led by cloud and AI-driven growth. Azure's accelerating revenue growth and Copilot adoption signal a strong enterprise AI transition. Sentiment is broadly positive, no major risk flags detected."},
    "tesla":{"company":"Tesla","ticker":"TSLA","sentiment_score":0.28,"sentiment_label":"Neutral","positive_pct":38,"neutral_pct":24,"negative_pct":38,"news_headlines":["Tesla misses delivery estimates for second consecutive quarter","Elon Musk announces new affordable EV model for 2025","Tesla faces increased competition from Chinese EV manufacturers","Autopilot investigation continues amid safety concerns","Tesla energy storage division posts record revenue"],"stock_price":245.30,"stock_change":"-2.1%","market_cap":"0.78T","pe_ratio":52.8,"week_high":298.43,"week_low":138.80,"recommendation":"Hold","analyst_target":260.0,"articles_analyzed":50,"report_text":"Tesla Inc. presents a mixed picture this week. While the energy storage division continues to perform well, vehicle delivery shortfalls and increasing competition from Chinese EV manufacturers have weighed on sentiment."},
}

def get_mock(company):
    return MOCK.get(company.lower().strip(), {
        "company":company,"ticker":"","sentiment_score":0.5,"sentiment_label":"Neutral",
        "positive_pct":50,"neutral_pct":35,"negative_pct":15,
        "news_headlines":[f"No mock data for {company}. Start the backend for live data."],
        "stock_price":0.0,"stock_change":"N/A","market_cap":"N/A","pe_ratio":"N/A",
        "week_high":"N/A","week_low":"N/A","recommendation":"N/A","analyst_target":0.0,
        "articles_analyzed":0,"report_text":f"Connect the FastAPI backend to get live analysis for {company}."
    })

def _pct(scores, mode):
    if not scores:
        return {"positive":50,"neutral":35,"negative":15}[mode]
    t = len(scores)
    if mode == "positive": return round(len([s for s in scores if s.get("score",0) >  0.2]) / t * 100)
    if mode == "negative": return round(len([s for s in scores if s.get("score",0) < -0.2]) / t * 100)
    return max(0, 100 - _pct(scores,"positive") - _pct(scores,"negative"))

def _fmt(v, bil=False):
    if v is None: return "N/A"
    if bil and isinstance(v, (int, float)):
        if v >= 1e12: return f"{v/1e12:.2f}T"
        if v >= 1e9:  return f"{v/1e9:.2f}B"
    if isinstance(v, float): return round(v, 2)
    return v

def translate(raw, company, ticker):
    scores = raw.get("sentiment_scores", [])
    price  = raw.get("current_price")
    prev   = raw.get("previous_close")
    chg    = "N/A"
    if price and prev:
        c   = ((price - prev) / prev) * 100
        chg = f"{'+' if c >= 0 else ''}{c:.1f}%"
    return {
        "company":          raw.get("company", company),
        "ticker":           ticker,
        "sentiment_score":  raw.get("overall_sentiment", 0.5),
        "sentiment_label":  raw.get("sentiment_label", "Neutral"),
        "positive_pct":     _pct(scores, "positive"),
        "neutral_pct":      _pct(scores, "neutral"),
        "negative_pct":     _pct(scores, "negative"),
        "news_headlines":   raw.get("top_headlines", []),
        "stock_price":      _fmt(price),
        "stock_change":     chg,
        "market_cap":       _fmt(raw.get("market_cap"), bil=True),
        "pe_ratio":         _fmt(raw.get("pe_ratio")),
        "week_high":        _fmt(raw.get("week_52_high")),
        "week_low":         _fmt(raw.get("week_52_low")),
        "recommendation":   raw.get("recommendation", "N/A"),
        "analyst_target":   _fmt(raw.get("analyst_target")),
        "articles_analyzed":raw.get("articles_analyzed", 0),
        "report_text":      raw.get("report", ""),
    }

def fetch(company):
    ticker = get_ticker(company)
    try:
        r = requests.post(
            "http://localhost:8000/analyze",
            json={"company": company, "ticker": ticker, "use_cache": True},
            timeout=60,
        )
        if r.status_code == 200:
            return translate(r.json(), company, ticker), False
    except Exception as e:
        print(f"Backend: {e}")
    return get_mock(company), True

def kw_check(data, keywords):
    text = " ".join(data.get("news_headlines",[])).lower() + " " + data.get("report_text","").lower()
    return [k for k in keywords if k.lower() in text]

def make_pdf(data):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=50)
    T = ParagraphStyle("T", fontSize=22, textColor=rl_colors.HexColor("#0B0F19"), fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)
    S = ParagraphStyle("S", fontSize=11, textColor=rl_colors.HexColor("#555"), fontName="Helvetica", alignment=TA_CENTER, spaceAfter=20)
    H = ParagraphStyle("H", fontSize=13, textColor=rl_colors.HexColor("#0077AA"), fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6)
    B = ParagraphStyle("B", fontSize=10, textColor=rl_colors.HexColor("#222"), fontName="Helvetica", leading=16, spaceAfter=5)
    ticker_str = f" ({data.get('ticker','')})" if data.get("ticker") else ""
    story = [
        Paragraph(f"Research Report: {data['company']}{ticker_str}", T),
        Paragraph(f"Articles analyzed: {data.get('articles_analyzed',0)}  |  FinResearch AI", S),
        Spacer(1, 8),
        Paragraph("Sentiment", H),
        Paragraph(f"Score: <b>{data['sentiment_score']:.2f}</b>  |  {data['sentiment_label']}  |  Positive: <b>{data['positive_pct']}%</b>  Neutral: <b>{data['neutral_pct']}%</b>  Negative: <b>{data['negative_pct']}%</b>", B),
        Spacer(1, 6),
        Paragraph("Market Data", H),
        Paragraph(f"Price: <b>${data['stock_price']}</b>  |  Change: <b>{data['stock_change']}</b>  |  Cap: <b>${data['market_cap']}</b>  |  P/E: <b>{data['pe_ratio']}</b>  |  52W High: <b>${data['week_high']}</b>  |  52W Low: <b>${data['week_low']}</b>  |  Recommendation: <b>{data.get('recommendation','N/A')}</b>", B),
        Spacer(1, 6),
        Paragraph("News Headlines", H),
    ]
    for i, h in enumerate(data.get("news_headlines", []), 1):
        story.append(Paragraph(f"{i}. {h}", B))
    story += [Spacer(1, 6), Paragraph("AI Analysis", H), Paragraph(data.get("report_text", ""), B)]
    doc.build(story)
    buf.seek(0)
    return buf

# ══════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📊 FinResearch AI")
    st.caption("Multi-Agent Financial Research")
    st.divider()
    st.markdown("**Mode**")
    mode = st.radio("mode", ["Single Company", "Compare Companies"], label_visibility="collapsed")
    st.divider()
    st.markdown("**🔔 Alert Keywords**")
    st.caption("Flagged if found in news:")
    kw_input = st.text_input("kw", "fraud, layoffs, lawsuit, bankruptcy, SEC", label_visibility="collapsed")
    st.divider()
    st.markdown("**Agent Pipeline**")
    for num, name, desc, col in [
        ("1", "News fetcher",    "NewsAPI",    "#4EEAFF"),
        ("2", "Sentiment AI",    "LLM scoring","#A78BFA"),
        ("3", "Market data",     "yfinance",   "#34D399"),
        ("4", "Report writer",   "LLM writer", "#FB923C"),
    ]:
        st.markdown(f"""<div style='display:flex;align-items:center;gap:9px;padding:5px 0'>
        <div style='width:22px;height:22px;border-radius:50%;background:{col};color:#0B0F19;font-size:.72rem;font-weight:800;display:flex;align-items:center;justify-content:center;flex-shrink:0'>{num}</div>
        <div><div style='font-size:.88rem;font-weight:600;color:#FFFFFF'>{name}</div><div style='font-size:.75rem;color:#5A7A9A'>{desc}</div></div>
        </div>""", unsafe_allow_html=True)
    st.divider()
    st.caption("LangGraph · FastAPI · Streamlit")

keywords = [k.strip() for k in kw_input.split(",") if k.strip()]

# ══════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════
st.markdown("<h1 style='color:#FFFFFF;font-size:1.7rem;font-weight:800;margin-bottom:2px'>📊 Financial Research Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#3A6080;font-size:.9rem;margin-bottom:1rem'>4 AI Agents — News · Sentiment · Market Data · Reports</p>", unsafe_allow_html=True)
st.divider()

# ══════════════════════════════════════════════════════════
# SINGLE COMPANY
# ══════════════════════════════════════════════════════════
if mode == "Single Company":
    c1, c2 = st.columns([5, 1])
    with c1:
        company = st.text_input("co", "", placeholder="Type any company name — Apple, Tesla, Nvidia, Reliance...", label_visibility="collapsed")
    with c2:
        run = st.button("Analyze →", type="primary")

    st.caption("Try: Apple · Microsoft · Tesla · Nvidia · Google · Amazon · Reliance · Infosys")

    if run and company.strip():
        pb = st.progress(0)
        st_txt = st.empty()
        for pct, msg in [(20,"Fetching news articles..."),(45,"Scoring sentiment with AI..."),(70,"Pulling live market data..."),(90,"Writing analyst report...")]:
            st_txt.markdown(f"<p style='color:#4EEAFF;font-size:.85rem'>{msg}</p>", unsafe_allow_html=True)
            pb.progress(pct)
            time.sleep(0.3)
        data, is_mock = fetch(company.strip())
        pb.progress(100)
        time.sleep(0.3)
        pb.empty()
        st_txt.empty()
        st.session_state.update({"data": data, "is_mock": is_mock})
    elif run:
        st.markdown('<div class="status-bar status-mock">Please type a company name first.</div>', unsafe_allow_html=True)

    data    = st.session_state.get("data", None)
    is_mock = st.session_state.get("is_mock", True)

    if data is None:
        st.markdown('<div class="status-bar status-mock" style="margin-top:1rem">👆 Enter a company name above and click Analyze →</div>', unsafe_allow_html=True)
        st.stop()

    # ── Status bar ────────────────────────────────────────
    triggered = kw_check(data, keywords)
    ticker    = data.get("ticker", "")
    ticker_info = f" · {ticker}" if ticker else ""

    if is_mock:
        st.markdown('<div class="status-bar status-mock">⚠ Mock data — start the FastAPI backend for live results</div>', unsafe_allow_html=True)
    elif triggered:
        st.markdown(f'<div class="status-bar status-risk">🚨 Risk keywords found — {", ".join(triggered)}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-bar status-live">✓ Live data{ticker_info} · {data.get("articles_analyzed",0)} articles analyzed · No risk keywords detected</div>', unsafe_allow_html=True)

    # ── Company title with optional ticker ────────────────
    ticker_pill = f'<span class="ticker-pill">{ticker}</span>' if ticker else ""
    st.markdown(f'<div class="company-title">{data["company"]} {ticker_pill}</div>', unsafe_allow_html=True)

    # ── Metrics ───────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Sentiment Score", f"{data['sentiment_score']:.2f}", data["sentiment_label"])
    m2.metric("Stock Price",     f"${data['stock_price']}",        data["stock_change"])
    m3.metric("Market Cap",      f"${data['market_cap']}")
    m4.metric("Recommendation",  str(data.get("recommendation", "N/A")))

    # ── Tabs ─────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["📰 News & Analysis", "📈 Sentiment", "💹 Market Data", "📥 Download PDF"])

    with tab1:
        left, right = st.columns([1, 1])
        with left:
            st.markdown('<div class="sec-label">Recent News Headlines</div>', unsafe_allow_html=True)
            for h in data.get("news_headlines", []):
                st.markdown(f'<div class="news-item"><div class="news-dot"></div><div class="news-text">{h}</div></div>', unsafe_allow_html=True)
        with right:
            st.markdown('<div class="sec-label">AI-Generated Analysis</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="card-wrap"><p style="color:#C8E0F4;line-height:1.85;font-size:.9rem">{data["report_text"]}</p></div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="sec-label">Sentiment Breakdown</div>', unsafe_allow_html=True)
        b1, b2 = st.columns([3, 1])
        with b1:
            st.markdown(f"<p style='color:#34D399;font-weight:700;margin-bottom:4px'>Positive — {data['positive_pct']}%</p>", unsafe_allow_html=True)
            st.progress(data["positive_pct"] / 100)
            st.markdown(f"<p style='color:#6A8FAF;font-weight:700;margin-bottom:4px'>Neutral — {data['neutral_pct']}%</p>", unsafe_allow_html=True)
            st.progress(data["neutral_pct"] / 100)
            st.markdown(f"<p style='color:#F87171;font-weight:700;margin-bottom:4px'>Negative — {data['negative_pct']}%</p>", unsafe_allow_html=True)
            st.progress(data["negative_pct"] / 100)
        with b2:
            st.metric("Positive", f"{data['positive_pct']}%")
            st.metric("Neutral",  f"{data['neutral_pct']}%")
            st.metric("Negative", f"{data['negative_pct']}%")

        st.markdown('<div class="sec-label" style="margin-top:1.2rem">Keyword Watch</div>', unsafe_allow_html=True)
        all_text = " ".join(data.get("news_headlines", [])).lower()
        chips = "".join(
            f'<span class="chip-bad">⚠ {k}</span>' if k.lower() in all_text
            else f'<span class="chip-ok">✓ {k}</span>'
            for k in keywords
        )
        st.markdown(chips, unsafe_allow_html=True)

    with tab3:
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Stock Price",    f"${data['stock_price']}", data["stock_change"])
        r2.metric("Market Cap",     f"${data['market_cap']}")
        r3.metric("P/E Ratio",      str(data["pe_ratio"]))
        r4.metric("Analyst Target", f"${data.get('analyst_target','N/A')}")

        st.markdown('<div class="sec-label" style="margin-top:1rem">52-Week Range</div>', unsafe_allow_html=True)
        w1, w2, w3 = st.columns(3)
        w1.metric("52W High",       f"${data['week_high']}")
        w2.metric("52W Low",        f"${data['week_low']}")
        w3.metric("Recommendation", str(data.get("recommendation", "N/A")))

    with tab4:
        st.markdown('<div class="pdf-label">Download Research Report as PDF</div>', unsafe_allow_html=True)
        st.markdown('<div class="pdf-sub">Includes sentiment analysis, market data, all headlines, and the full AI-written report.</div>', unsafe_allow_html=True)
        with st.expander("Preview report before downloading", expanded=False):
            ticker_str = f"({ticker})" if ticker else ""
            st.markdown(f"**{data['company']} {ticker_str} — Research Report**")
            st.divider()
            st.markdown(f"Sentiment: **{data['sentiment_label']}** ({data['sentiment_score']:.2f}) · Stock: **${data['stock_price']}** {data['stock_change']} · Cap: **${data['market_cap']}**")
            st.divider()
            for h in data.get("news_headlines", []):
                st.markdown(f"- {h}")
            st.divider()
            st.markdown(f"<p style='color:#C8E0F4;line-height:1.85'>{data['report_text']}</p>", unsafe_allow_html=True)

        pdf = make_pdf(data)
        st.download_button(
            f"↓ Download {data['company']} Report — PDF",
            data=pdf,
            file_name=f"{data['company']}_research_report.pdf",
            mime="application/pdf"
        )

# ══════════════════════════════════════════════════════════
# COMPARE MODE
# ══════════════════════════════════════════════════════════
else:
    st.markdown("<p style='color:#FFFFFF;font-size:1rem;font-weight:700;margin-bottom:.5rem'>Compare Multiple Companies</p>", unsafe_allow_html=True)
    st.markdown("<p style='color:#3A6080;font-size:.85rem;margin-bottom:1rem'>Enter 2–3 company names separated by commas.</p>", unsafe_allow_html=True)

    ci, cb = st.columns([5, 1])
    with ci:
        ci_val = st.text_input("cmp", "Apple, Microsoft, Tesla", placeholder="Apple, Microsoft, Tesla", label_visibility="collapsed")
    with cb:
        run_cmp = st.button("Compare →", type="primary")

    if run_cmp:
        cos = [c.strip() for c in ci_val.split(",") if c.strip()]
        if len(cos) < 2:
            st.markdown('<div class="status-bar status-mock">Enter at least 2 companies.</div>', unsafe_allow_html=True)
        else:
            results, any_mock = {}, False
            pb = st.progress(0)
            stxt = st.empty()
            for i, co in enumerate(cos):
                stxt.markdown(f"<p style='color:#4EEAFF;font-size:.85rem'>Analyzing {co}...</p>", unsafe_allow_html=True)
                d, mock = fetch(co)
                results[co] = d
                if mock: any_mock = True
                pb.progress(int((i + 1) / len(cos) * 100))
            pb.empty()
            stxt.empty()
            st.session_state.update({"cmp_results": results, "cmp_mock": any_mock})

    results  = st.session_state.get("cmp_results", {})
    any_mock = st.session_state.get("cmp_mock", False)

    if results:
        cos = list(results.keys())
        if any_mock:
            st.markdown('<div class="status-bar status-mock">⚠ Mock data — backend not connected.</div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-label" style="margin-top:.5rem">Side-by-Side Metrics</div>', unsafe_allow_html=True)
        cols = st.columns(len(cos))
        for i, co in enumerate(cos):
            d = results[co]
            tk = d.get("ticker","")
            with cols[i]:
                tk_display = f'<span style="color:#2A5070;font-size:.78rem;font-family:monospace"> {tk}</span>' if tk else ""
                st.markdown(f"<p style='color:#4EEAFF;font-weight:800;font-size:.95rem;margin-bottom:8px'>{d['company']}{tk_display}</p>", unsafe_allow_html=True)
                st.metric("Sentiment",   f"{d['sentiment_score']:.2f}", d["sentiment_label"])
                st.metric("Stock Price", f"${d['stock_price']}",        d["stock_change"])
                st.metric("Market Cap",  f"${d['market_cap']}")
                st.metric("Recomm.",     str(d.get("recommendation", "N/A")))

        st.markdown('<div class="sec-label" style="margin-top:1rem">Sentiment Comparison</div>', unsafe_allow_html=True)
        st.bar_chart({co: results[co]["sentiment_score"] for co in cos})

        st.markdown('<div class="sec-label" style="margin-top:1rem">Latest Headlines</div>', unsafe_allow_html=True)
        cols2 = st.columns(len(cos))
        for i, co in enumerate(cos):
            with cols2[i]:
                st.markdown(f"<p style='color:#4EEAFF;font-weight:700;margin-bottom:6px'>{co}</p>", unsafe_allow_html=True)
                for h in results[co].get("news_headlines", [])[:3]:
                    st.markdown(f'<div class="news-item"><div class="news-dot"></div><div class="news-text">{h}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-label" style="margin-top:1rem">AI Summary</div>', unsafe_allow_html=True)
        best  = max(results, key=lambda c: results[c]["sentiment_score"])
        worst = min(results, key=lambda c: results[c]["sentiment_score"])
        st.markdown(
            f'<div class="card-wrap"><p style="color:#C8E0F4;line-height:1.85">'
            f'<span style="color:#34D399;font-weight:700">{best}</span> shows the strongest positive sentiment '
            f'({results[best]["sentiment_score"]:.2f}, recommendation: {results[best].get("recommendation","N/A")}). '
            f'<span style="color:#FB923C;font-weight:700">{worst}</span> has the lowest score '
            f'({results[worst]["sentiment_score"]:.2f}). AI summary only.</p></div>',
            unsafe_allow_html=True)

        st.markdown('<div class="sec-label">Keyword Alerts</div>', unsafe_allow_html=True)
        for co in cos:
            t = kw_check(results[co], keywords)
            if t:
                st.markdown(f'<div class="status-bar status-risk">🚨 {co}: {", ".join(t)}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="status-bar status-live">✓ {co}: No risk keywords detected</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
