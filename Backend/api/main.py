import sys
import os
sys.path.append(".")

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
from dotenv import load_dotenv

load_dotenv()

# ── Import pipeline and PDF generator ────────────────────────────────────────
from Backend.workflows.graph import run_research_pipeline
from Backend.api.pdf_generator import generate_pdf

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Financial Research Assistant API",
    description="Multi-agent AI system for financial research — powered by LangGraph",
    version="1.0.0",
)


# ── Request/Response Models ───────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    company: str                    # e.g. "Apple"
    ticker:  str                    # e.g. "AAPL"
    use_cache: Optional[bool] = True

class SentimentScore(BaseModel):
    title:  str
    source: str
    score:  float

class AnalyzeResponse(BaseModel):
    company:             str
    ticker:              str
    overall_sentiment:   float
    sentiment_label:     str
    articles_analyzed:   int
    current_price:       Optional[float]
    market_cap:          Optional[float]
    pe_ratio:            Optional[float]
    recommendation:      Optional[str]
    analyst_target:      Optional[float]
    report:              str
    top_headlines:       list


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "status":  "running",
        "message": "Financial Research Assistant API is live 🚀",
        "endpoints": [
            "POST /analyze     → run full research pipeline",
            "POST /download-pdf → download PDF report",
            "GET  /health      → health check",
        ]
    }

@app.get("/health")
def health():
    return {"status": "healthy"}


# ── Main endpoint: Run full pipeline ─────────────────────────────────────────
@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    """
    Runs the full 4-agent pipeline for a given company.
    Returns sentiment scores, market data, and AI-generated report.
    """
    if not request.company or not request.ticker:
        raise HTTPException(status_code=400, detail="Company and ticker are required.")

    try:
        # Run the full LangGraph pipeline
        result = run_research_pipeline(
            company=request.company,
            ticker=request.ticker,
            use_cache=request.use_cache,
        )

        # Extract market data safely
        market_data = result.get("market_data", {})

        # Get top 5 headlines for the response
        sentiment_scores = result.get("sentiment_scores", [])
        top_headlines = [
            s["title"] for s in sentiment_scores[:5]
        ]

        return {
            "company":            result.get("company"),
            "ticker":             request.ticker,
            "overall_sentiment":  result.get("overall_sentiment", 0.0),
            "sentiment_label":    result.get("sentiment_label", "Neutral"),
            "articles_analyzed":  len(sentiment_scores),
            "current_price":      market_data.get("current_price"),
            "market_cap":         market_data.get("market_cap"),
            "pe_ratio":           market_data.get("pe_ratio"),
            "week_52_high":       market_data.get("week_52_high"),
            "week_52_low":        market_data.get("week_52_low"),
            "revenue":            market_data.get("revenue"),
            "profit_margin":      market_data.get("profit_margin"),
            "recommendation":     market_data.get("recommendation"),
            "analyst_target":     market_data.get("analyst_target"),
            "report":             result.get("report", ""),
            "top_headlines":      top_headlines,
            "sentiment_scores":   sentiment_scores,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


# ── PDF Download endpoint ─────────────────────────────────────────────────────
@app.post("/download-pdf")
def download_pdf(request: AnalyzeRequest):
    """
    Runs the pipeline and returns a downloadable PDF report.
    Person B's Streamlit dashboard calls this for the download button.
    """
    if not request.company or not request.ticker:
        raise HTTPException(status_code=400, detail="Company and ticker are required.")

    try:
        # Run pipeline
        result = run_research_pipeline(
            company=request.company,
            ticker=request.ticker,
            use_cache=request.use_cache,
        )

        market_data      = result.get("market_data", {})
        sentiment_scores = result.get("sentiment_scores", [])

        # Calculate sentiment breakdown percentages
        total = len(sentiment_scores)
        if total > 0:
            positive_pct = round(len([s for s in sentiment_scores if s["score"] > 0.2]) / total * 100)
            negative_pct = round(len([s for s in sentiment_scores if s["score"] < -0.2]) / total * 100)
            neutral_pct  = 100 - positive_pct - negative_pct
        else:
            positive_pct = neutral_pct = negative_pct = 0

        # Build PDF data dict
        pdf_data = {
            "company":         request.company,
            "ticker":          request.ticker,
            "sentiment_score": result.get("overall_sentiment", 0.0),
            "sentiment_label": result.get("sentiment_label", "Neutral"),
            "positive_pct":    positive_pct,
            "neutral_pct":     neutral_pct,
            "negative_pct":    negative_pct,
            "news_headlines":  [s["title"] for s in sentiment_scores[:5]],
            "stock_price":     market_data.get("current_price", "N/A"),
            "stock_change":    "N/A",
            "market_cap":      market_data.get("market_cap", "N/A"),
            "pe_ratio":        market_data.get("pe_ratio", "N/A"),
            "week_high":       market_data.get("week_52_high", "N/A"),
            "week_low":        market_data.get("week_52_low", "N/A"),
            "report_text":     result.get("report", ""),
        }

        # Generate PDF buffer
        pdf_buffer = generate_pdf(pdf_data)

        # Return as downloadable file
        filename = f"{request.company.replace(' ', '_')}_research_report.pdf"
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")


# ── Compare multiple companies ────────────────────────────────────────────────
@app.post("/compare")
def compare(companies: list[dict]):
    """
    Runs pipeline for multiple companies and returns side-by-side comparison.
    Example input: [{"company": "Apple", "ticker": "AAPL"},
                    {"company": "Microsoft", "ticker": "MSFT"}]
    """
    if len(companies) < 2:
        raise HTTPException(status_code=400, detail="Provide at least 2 companies to compare.")
    if len(companies) > 4:
        raise HTTPException(status_code=400, detail="Maximum 4 companies allowed.")

    results = []
    for item in companies:
        try:
            result = run_research_pipeline(
                company=item.get("company", ""),
                ticker=item.get("ticker", ""),
                use_cache=True,
            )
            market_data = result.get("market_data", {})
            results.append({
                "company":           item.get("company"),
                "ticker":            item.get("ticker"),
                "overall_sentiment": result.get("overall_sentiment", 0.0),
                "sentiment_label":   result.get("sentiment_label", "Neutral"),
                "current_price":     market_data.get("current_price"),
                "market_cap":        market_data.get("market_cap"),
                "pe_ratio":          market_data.get("pe_ratio"),
                "recommendation":    market_data.get("recommendation"),
                "analyst_target":    market_data.get("analyst_target"),
                "report":            result.get("report", ""),
            })
        except Exception as e:
            results.append({
                "company": item.get("company"),
                "ticker":  item.get("ticker"),
                "error":   str(e),
            })

    return {"comparison": results}


# ── Run server ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("Backend.api.main:app", host="0.0.0.0", port=8000, reload=True):