import os
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()


def _auto_detect_ticker(company: str) -> str | None:
    """Auto-detect ticker symbol from company name using yfinance Search."""
    try:
        results = yf.Search(company).quotes
        if results:
            ticker = results[0]["symbol"]
            print(f"[MarketDataAgent] Auto-detected ticker: {ticker} for '{company}'")
            return ticker
    except Exception as e:
        print(f"[MarketDataAgent] Could not auto-detect ticker: {e}")
    return None


def market_data_agent(state: dict) -> dict:
    """
    Agent 3 — Market Data
    Fetches real-time stock price and financial info using yfinance.
    Receives: state with 'ticker' key (optional — auto-detected if missing)
    Returns: state updated with 'market_data' key
    """
    ticker  = state.get("ticker", "")
    company = state.get("company", "")

    # ── Auto-detect ticker if not provided ───────────────────────────────────
    if not ticker:
        ticker = _auto_detect_ticker(company)
        if not ticker:
            return {
                **state,
                "market_data": {},
                "error": f"Could not find ticker for '{company}'. Please provide it manually."
            }

    print(f"[MarketDataAgent] Fetching market data for '{ticker}'...")

    try:
        stock = yf.Ticker(ticker)
        info  = stock.info

        # Extract the most useful fields for financial analysis
        market_data = {
            # Basic info
            "company_name":       info.get("longName", company),
            "ticker":             ticker,
            "sector":             info.get("sector", "N/A"),
            "industry":           info.get("industry", "N/A"),
            "country":            info.get("country", "N/A"),
            "website":            info.get("website", "N/A"),

            # Price data
            "current_price":      info.get("currentPrice")      or info.get("regularMarketPrice", "N/A"),
            "previous_close":     info.get("previousClose", "N/A"),
            "open_price":         info.get("open", "N/A"),
            "day_high":           info.get("dayHigh", "N/A"),
            "day_low":            info.get("dayLow", "N/A"),
            "week_52_high":       info.get("fiftyTwoWeekHigh", "N/A"),
            "week_52_low":        info.get("fiftyTwoWeekLow", "N/A"),

            # Valuation
            "market_cap":         info.get("marketCap", "N/A"),
            "pe_ratio":           info.get("trailingPE", "N/A"),
            "forward_pe":         info.get("forwardPE", "N/A"),
            "price_to_book":      info.get("priceToBook", "N/A"),
            "enterprise_value":   info.get("enterpriseValue", "N/A"),

            # Financials
            "revenue":            info.get("totalRevenue", "N/A"),
            "gross_profit":       info.get("grossProfits", "N/A"),
            "net_income":         info.get("netIncomeToCommon", "N/A"),
            "profit_margin":      info.get("profitMargins", "N/A"),
            "revenue_growth":     info.get("revenueGrowth", "N/A"),
            "earnings_growth":    info.get("earningsGrowth", "N/A"),

            # Dividends & shares
            "dividend_yield":     info.get("dividendYield", "N/A"),
            "shares_outstanding": info.get("sharesOutstanding", "N/A"),

            # Analyst targets
            "analyst_target":     info.get("targetMeanPrice", "N/A"),
            "recommendation":     info.get("recommendationKey", "N/A"),
        }

        # Format large numbers for readability
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
            return val

        print(f"[MarketDataAgent] ✅ Data fetched for {market_data['company_name']}")
        print(f"  Current Price   : ${market_data['current_price']}")
        print(f"  Market Cap      : {fmt(market_data['market_cap'])}")
        print(f"  P/E Ratio       : {market_data['pe_ratio']}")
        print(f"  Revenue         : {fmt(market_data['revenue'])}")
        print(f"  Recommendation  : {market_data['recommendation']}")

        # Update state ticker in case it was auto-detected
        return {**state, "ticker": ticker, "market_data": market_data}

    except Exception as e:
        print(f"[MarketDataAgent] Error fetching data: {e}")
        return {**state, "market_data": {}, "error": str(e)}


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test 1 — with ticker provided
    print("=== Test 1: With ticker ===")
    result = market_data_agent({"company": "Apple", "ticker": "AAPL"})
    print(f"Price: ${result['market_data'].get('current_price')}")

    # Test 2 — without ticker (auto-detect)
    print("\n=== Test 2: Without ticker (auto-detect) ===")
    result = market_data_agent({"company": "JP Morgan", "ticker": ""})
    print(f"Auto ticker : {result.get('ticker')}")
    print(f"Price       : ${result['market_data'].get('current_price')}")
    print(f"Company     : {result['market_data'].get('company_name')}")