import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def sentiment_agent(state: dict) -> dict:
    """
    Agent 2 — Sentiment Analyzer
    Reads each article and scores sentiment from -1.0 (very negative) to +1.0 (very positive).
    Receives: state with 'articles' key
    Returns: state updated with 'sentiment_scores', 'overall_sentiment', 'sentiment_label' keys
    """
    articles = state.get("articles", [])
    company  = state.get("company", "the company")

    if not articles:
        return {
            **state,
            "sentiment_scores":   [],
            "overall_sentiment":  0.0,
            "sentiment_label":    "Neutral",
            "sentiment_summary":  "No articles found to analyze.",
        }

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    sentiment_scores = []

    print(f"[SentimentAgent] Analyzing {len(articles)} articles...")

    for i, article in enumerate(articles):
        # Combine title + description for analysis
        text = f"Title: {article.get('title', '')}\nDescription: {article.get('description', '')}"

        if not text.strip() or text == "Title: \nDescription: ":
            continue

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a financial sentiment analyst. "
                            "Given a news article about a company, return ONLY a number "
                            "between -1.0 and 1.0 representing the sentiment. "
                            "-1.0 = very negative (bankruptcy, fraud, huge losses), "
                            "0.0 = neutral (routine news), "
                            "+1.0 = very positive (record profits, major wins). "
                            "Return ONLY the number. No explanation. No text."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Company: {company}\n\n{text}",
                    },
                ],
                max_tokens=10,
                temperature=0,             # deterministic output
            )

            score_str = response.choices[0].message.content.strip()
            score = float(score_str)
            score = max(-1.0, min(1.0, score))   # clamp between -1 and 1

            sentiment_scores.append({
                "title":  article.get("title", ""),
                "source": article.get("source", ""),
                "score":  score,
            })

            print(f"  [{i+1}/{len(articles)}] Score: {score:+.2f} | {article.get('title', '')[:60]}...")

        except Exception as e:
            print(f"  [{i+1}] Skipped (error: {e})")
            continue

    if not sentiment_scores:
        return {
            **state,
            "sentiment_scores":   [],
            "overall_sentiment":  0.0,
            "sentiment_label":    "Neutral",
            "sentiment_summary":  "Could not analyze any articles.",
        }

    # Calculate overall sentiment (average of all scores)
    overall = round(sum(s["score"] for s in sentiment_scores) / len(sentiment_scores), 3)

    # Label based on score range
    if overall >= 0.3:
        label = "Positive 📈"
    elif overall <= -0.3:
        label = "Negative 📉"
    else:
        label = "Neutral ➡️"

    # Find most positive and most negative article
    most_positive = max(sentiment_scores, key=lambda x: x["score"])
    most_negative = min(sentiment_scores, key=lambda x: x["score"])

    print(f"\n[SentimentAgent] Overall sentiment for '{company}': {overall:+.3f} → {label}")

    return {
        **state,
        "sentiment_scores":   sentiment_scores,
        "overall_sentiment":  overall,
        "sentiment_label":    label,
        "most_positive":      most_positive,
        "most_negative":      most_negative,
    }


# ── Quick test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Import news fetcher to get real articles
    import sys
    sys.path.append("")
    from Backend.agents.news_fetcher import news_fetcher_agent

    # Step 1: Fetch articles (uses cache if available)
    state = {"company": "Apple", "ticker": "AAPL"}
    state = news_fetcher_agent(state, use_cache=True)

    # Step 2: Run sentiment analysis
    state = sentiment_agent(state)

    # Step 3: Print results
    print("\n========== SENTIMENT RESULTS ==========")
    print(f"Company         : {state['company']}")
    print(f"Articles scored : {len(state['sentiment_scores'])}")
    print(f"Overall score   : {state['overall_sentiment']:+.3f}")
    print(f"Sentiment label : {state['sentiment_label']}")
    print(f"\nMost positive   : {state['most_positive']['title'][:70]}...")
    print(f"Score           : {state['most_positive']['score']:+.2f}")
    print(f"\nMost negative   : {state['most_negative']['title'][:70]}...")
    print(f"Score           : {state['most_negative']['score']:+.2f}")