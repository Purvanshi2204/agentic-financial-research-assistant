import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

def market_data_agent(state: dict) -> dict:
    """
    Agent 3 — Market Data
    Fetches real-time stock price and financial info using yfinance.
    Receives: state with 'ticker' key
    Returns: state updated with 'market_data' key
    """
    ticker  = state.get("ticker", "")
    company = state.get("company", "")

    if not ticker:
        return {**state, "market_data": {}, "error": "No ticker symbol provided."}

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

        return {**state, "market_data": market_data}

    except Exception as e:
        print(f"[MarketDataAgent] Error fetching data: {e}")
        return {**state, "market_data": {}, "error": str(e)}


# ── Quick test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_state = {"company": "Apple", "ticker": "AAPL"}
    result = market_data_agent(test_state)

    print("\n========== MARKET DATA RESULTS ==========")
    for key, value in result["market_data"].items():
        print(f"{key:<25}: {value}")