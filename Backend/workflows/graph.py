from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# ── Import all 4 agents ───────────────────────────────────────────────────────
import sys
sys.path.append(".")
from Backend.agents.news_fetcher import news_fetcher_agent
from Backend.agents.sentiment_agent import sentiment_agent
from Backend.agents.market_data_agent import market_data_agent
from Backend.agents.report_writer import report_writer_agent


# ── Define the state schema ───────────────────────────────────────────────────
# This is the shared dictionary that gets passed between all agents
class ResearchState(TypedDict, total=False):
    # Input
    company:            str
    ticker:             str

    # Agent 1 output
    articles:           List[Dict[str, Any]]

    # Agent 2 output
    sentiment_scores:   List[Dict[str, Any]]
    overall_sentiment:  float
    sentiment_label:    str
    most_positive:      Dict[str, Any]
    most_negative:      Dict[str, Any]

    # Agent 3 output
    market_data:        Dict[str, Any]

    # Agent 4 output
    report:             str

    # Error handling
    error:              str


# ── Wrap each agent for LangGraph ────────────────────────────────────────────
def run_news_fetcher(state: ResearchState) -> ResearchState:
    print("\n🔵 Step 1/4: Fetching news...")
    return news_fetcher_agent(state, use_cache=True)

def run_sentiment_agent(state: ResearchState) -> ResearchState:
    print("\n🟡 Step 2/4: Analyzing sentiment...")
    return sentiment_agent(state)

def run_market_data_agent(state: ResearchState) -> ResearchState:
    print("\n🟢 Step 3/4: Fetching market data...")
    return market_data_agent(state)

def run_report_writer(state: ResearchState) -> ResearchState:
    print("\n🔴 Step 4/4: Writing analyst report...")
    return report_writer_agent(state)


# ── Build the LangGraph pipeline ─────────────────────────────────────────────
def build_graph():
    graph = StateGraph(ResearchState)

    # Add all 4 agents as nodes
    graph.add_node("fetch_news",      run_news_fetcher)
    graph.add_node("analyze_sentiment", run_sentiment_agent)
    graph.add_node("get_market_data", run_market_data_agent)
    graph.add_node("write_report",    run_report_writer)

    # Define the flow: Agent1 → Agent2 → Agent3 → Agent4 → END
    graph.set_entry_point("fetch_news")
    graph.add_edge("fetch_news",        "analyze_sentiment")
    graph.add_edge("analyze_sentiment", "get_market_data")
    graph.add_edge("get_market_data",   "write_report")
    graph.add_edge("write_report",      END)

    return graph.compile()


# ── The main function FastAPI will call ──────────────────────────────────────
def run_research_pipeline(company: str, ticker: str, use_cache: bool = True) -> dict:
    """
    Runs the full 4-agent pipeline for a given company.
    Returns the complete state with report, sentiment, and market data.
    """
    app = build_graph()

    initial_state = {
        "company": company,
        "ticker":  ticker,
    }

    print(f"\n{'='*50}")
    print(f"  Running Research Pipeline for {company} ({ticker})")
    print(f"{'='*50}")

    final_state = app.invoke(initial_state)

    print(f"\n{'='*50}")
    print(f"  ✅ Pipeline Complete!")
    print(f"{'='*50}\n")

    return final_state


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    result = run_research_pipeline("Apple", "AAPL")

    print("\n========== PIPELINE SUMMARY ==========")
    print(f"Company          : {result.get('company')}")
    print(f"Articles fetched : {len(result.get('articles', []))}")
    print(f"Sentiment score  : {result.get('overall_sentiment'):+.3f}")
    print(f"Sentiment label  : {result.get('sentiment_label')}")
    print(f"Current price    : ${result.get('market_data', {}).get('current_price')}")
    print(f"Recommendation   : {result.get('market_data', {}).get('recommendation')}")
    print(f"\n--- REPORT PREVIEW (first 500 chars) ---")
    print(result.get("report", "")[:500])