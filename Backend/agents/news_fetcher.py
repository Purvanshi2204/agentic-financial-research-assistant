import os
import json
import time
from newsapi import NewsApiClient
from dotenv import load_dotenv

load_dotenv()

CACHE_DIR          = "utils/news_cache"
CACHE_EXPIRY_HOURS = 12      # cache expires after 12 hours → fresh data fetched


def _cache_path(company: str) -> str:
    """Returns the file path for a company's cached news."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    safe_name = company.lower().replace(" ", "_")
    return f"{CACHE_DIR}/{safe_name}.json"


def _is_cache_valid(company: str) -> bool:
    """Check if cache file exists AND is less than 12 hours old."""
    path = _cache_path(company)
    if not os.path.exists(path):
        return False
    file_age_hours = (time.time() - os.path.getmtime(path)) / 3600
    return file_age_hours < CACHE_EXPIRY_HOURS


def _load_from_cache(company: str) -> list | None:
    """Load articles from cache only if cache is still valid."""
    if not _is_cache_valid(company):
        print(f"[NewsFetcher] Cache expired for '{company}' → fetching fresh data")
        return None
    with open(_cache_path(company), "r") as f:
        print(f"[NewsFetcher] Loaded '{company}' articles from cache (valid, no API call)")
        return json.load(f)


def _save_to_cache(company: str, articles: list):
    """Save fetched articles to cache."""
    path = _cache_path(company)
    with open(path, "w") as f:
        json.dump(articles, f, indent=2)
    print(f"[NewsFetcher] Saved {len(articles)} articles to cache → {path}")


def news_fetcher_agent(state: dict, use_cache: bool = True) -> dict:
    """
    Agent 1 — News Fetcher
    Fetches latest news articles for a given company using NewsAPI.
    Receives: state with 'company' and optional 'ticker' keys
    Returns: state updated with 'articles' key

    use_cache=True  → loads from file if valid (< 12 hours old)
    use_cache=False → always hits the real NewsAPI (use for final demo)
    """
    company = state.get("company", "")
    ticker  = state.get("ticker", "")

    if not company:
        return {**state, "articles": [], "error": "No company name provided."}

    # ── Try cache first (only if valid) ─────────────────────────────────────
    if use_cache:
        cached = _load_from_cache(company)
        if cached:
            return {**state, "articles": cached}

    # ── Hit real API ─────────────────────────────────────────────────────────
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        raise ValueError("NEWS_API_KEY not found in .env file")

    newsapi = NewsApiClient(api_key=api_key)

    # Use ticker if provided for more precise results
    query = f'"{company}"' if not ticker else f'"{company}" OR "{ticker}"'

    try:
        response = newsapi.get_everything(
            q=query,
            language="en",
            sort_by="relevancy",
            page_size=50,
        )

        articles = response.get("articles", [])

        # Extract only what we need
        cleaned = []
        for article in articles:
            cleaned.append({
                "title":        article.get("title", ""),
                "description":  article.get("description", ""),
                "content":      article.get("content", ""),
                "url":          article.get("url", ""),
                "published_at": article.get("publishedAt", ""),
                "source":       article.get("source", {}).get("name", ""),
            })

        print(f"[NewsFetcher] Fetched {len(cleaned)} articles for '{company}' from API")

        # Save fresh data to cache
        _save_to_cache(company, cleaned)

        return {**state, "articles": cleaned}

    except Exception as e:
        print(f"[NewsFetcher] Error fetching news: {e}")
        return {**state, "articles": [], "error": str(e)}


# ── Quick test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_state = {"company": "Apple", "ticker": "AAPL"}

    result = news_fetcher_agent(test_state, use_cache=True)

    print(f"\nTotal articles fetched: {len(result['articles'])}")
    for i, article in enumerate(result["articles"][:3], 1):
        print(f"\n--- Article {i} ---")
        print(f"Source : {article['source']}")
        print(f"Title  : {article['title']}")
        print(f"Date   : {article['published_at']}")
        print(f"URL    : {article['url']}")

    # ── To force a fresh API call regardless of cache age ──
    # result = news_fetcher_agent(test_state, use_cache=False)