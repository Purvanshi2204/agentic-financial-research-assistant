import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def report_writer_agent(state: dict) -> dict:
    """
    Agent 4 — Report Writer
    Takes all data from Agents 1, 2, 3 and writes a full analyst report.
    Receives: state with 'company', 'articles', 'sentiment_scores',
              'overall_sentiment', 'sentiment_label', 'market_data' keys
    Returns: state updated with 'report' key
    """
    company          = state.get("company", "the company")
    ticker           = state.get("ticker", "")
    overall_sentiment = state.get("overall_sentiment", 0.0)
    sentiment_label  = state.get("sentiment_label", "Neutral")
    market_data      = state.get("market_data", {})
    sentiment_scores = state.get("sentiment_scores", [])
    most_positive    = state.get("most_positive", {})
    most_negative    = state.get("most_negative", {})

    if not market_data:
        return {**state, "report": "Error: No market data available to generate report."}

    print(f"[ReportWriter] Generating analyst report for '{company}'...")

    # ── Format market data for the prompt ────────────────────────────────────
    def fmt(val):
        if isinstance(val, (int, float)):
            if val >= 1_000_000_000_000:
                return f"${val/1_000_000_000_000:.2f}T"
            elif val >= 1_000_000_000:
                return f"${val/1_000_000_000:.2f}B"
            elif val >= 1_000_000:
                return f"${val/1_000_000:.2f}M"
            else:
                return f"${val:,.2f}"
        return str(val)

    # Top 5 most positive and negative headlines for context
    top_positive = sorted(sentiment_scores, key=lambda x: x["score"], reverse=True)[:3]
    top_negative = sorted(sentiment_scores, key=lambda x: x["score"])[:3]

    positive_headlines = "\n".join([f"  - {a['title']} (score: {a['score']:+.2f})" for a in top_positive])
    negative_headlines = "\n".join([f"  - {a['title']} (score: {a['score']:+.2f})" for a in top_negative])

    prompt = f"""
You are a senior financial analyst at JP Morgan. Write a professional equity research report for {company} ({ticker}).

Use ONLY the data provided below. Be specific, cite numbers, and write like a real analyst.

=== MARKET DATA ===
Company        : {market_data.get('company_name', company)}
Sector         : {market_data.get('sector', 'N/A')}
Industry       : {market_data.get('industry', 'N/A')}
Current Price  : ${market_data.get('current_price', 'N/A')}
52-Week High   : ${market_data.get('week_52_high', 'N/A')}
52-Week Low    : ${market_data.get('week_52_low', 'N/A')}
Market Cap     : {fmt(market_data.get('market_cap', 'N/A'))}
P/E Ratio      : {market_data.get('pe_ratio', 'N/A')}
Forward P/E    : {market_data.get('forward_pe', 'N/A')}
Revenue        : {fmt(market_data.get('revenue', 'N/A'))}
Net Income     : {fmt(market_data.get('net_income', 'N/A'))}
Profit Margin  : {market_data.get('profit_margin', 'N/A')}
Revenue Growth : {market_data.get('revenue_growth', 'N/A')}
Analyst Target : ${market_data.get('analyst_target', 'N/A')}
Recommendation : {market_data.get('recommendation', 'N/A')}

=== NEWS SENTIMENT ===
Overall Sentiment Score : {overall_sentiment:+.3f} ({sentiment_label})
Articles Analyzed       : {len(sentiment_scores)}

Top Positive Headlines:
{positive_headlines}

Top Negative Headlines:
{negative_headlines}

=== REPORT FORMAT ===
Write the report in exactly this structure:

**EQUITY RESEARCH REPORT — {company.upper()} ({ticker})**
Date: {__import__('datetime').date.today().strftime('%B %d, %Y')}

**1. EXECUTIVE SUMMARY**
(2-3 sentences: overall outlook, buy/hold/sell recommendation, price target)

**2. FINANCIAL PERFORMANCE**
(3-4 sentences: revenue, profit margin, P/E ratio, growth metrics with specific numbers)

**3. NEWS SENTIMENT ANALYSIS**
(3-4 sentences: overall sentiment score, what's driving positive/negative news, key headlines)

**4. VALUATION & PRICE TARGET**
(2-3 sentences: current price vs analyst target, upside/downside %, valuation commentary)

**5. KEY RISKS**
(3 bullet points of specific risks based on the negative headlines and market data)

**6. INVESTMENT RECOMMENDATION**
(2-3 sentences: final clear recommendation with reasoning)

Write professionally. Use specific numbers. Do not add any text outside this structure.
"""

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior equity research analyst at JP Morgan. Write precise, data-driven financial reports.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            max_tokens=1000,
            temperature=0.3,
        )

        report = response.choices[0].message.content.strip()
        print(f"[ReportWriter] ✅ Report generated ({len(report)} characters)")

        return {**state, "report": report}

    except Exception as e:
        print(f"[ReportWriter] Error generating report: {e}")
        return {**state, "report": f"Error generating report: {e}"}


# ── Quick test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.path.append(".")
    from Backend.agents.news_fetcher import news_fetcher_agent
    from Backend.agents.sentiment_agent import sentiment_agent
    from Backend.agents.market_data_agent import market_data_agent

    # Run all 3 agents first
    state = {"company": "Apple", "ticker": "AAPL"}
    state = news_fetcher_agent(state, use_cache=True)
    state = sentiment_agent(state)
    state = market_data_agent(state)

    # Now generate the report
    state = report_writer_agent(state)

    print("\n========== FINAL ANALYST REPORT ==========\n")
    print(state["report"])