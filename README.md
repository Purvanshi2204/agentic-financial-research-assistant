# Agentic Financial Research Assistant

We built this for our placement prep — basically an AI system that does what a stock market analyst does, but automatically. You give it a company name and it fetches the latest news, figures out if the sentiment is positive or negative, grabs the stock data, and writes a full research report. All in under 30 seconds.

Built using Python, FastAPI, LangGraph, and Streamlit.

---

## What it does

- Fetches live news articles about any company using NewsAPI
- Runs sentiment analysis on the news using an LLM
- Pulls stock price, market cap, P/E ratio from Yahoo Finance
- Generates an AI-written research report
- Lets you compare 2-3 companies side by side
- Alerts you if risky keywords like "fraud" or "layoffs" show up in the news
- Exports everything as a downloadable PDF

---

## How the agents work

We used LangGraph to connect 4 agents in a pipeline:

```
News Fetcher → Sentiment Analyzer → Market Data → Report Writer
```

Each agent does one job and passes its output to the next one. The final output is a structured report with all the data combined.

---

## Tech stack

- **LangGraph** — for building the multi-agent workflow
- **FastAPI** — backend API
- **Streamlit** — frontend dashboard
- **NewsAPI** — for fetching financial news
- **yfinance** — for stock market data
- **OpenAI API** — for sentiment analysis and report generation
- **ReportLab** — for PDF export

---

## Project structure

```
agentic-financial-research-assistant/
├── agents/
│   ├── news_fetcher.py
│   ├── sentiment_agent.py
│   ├── market_data_agent.py
│   └── report_writer.py
├── api/
│   ├── main.py
│   └── pdf_generator.py
├── workflows/
│   └── graph.py
├── frontend/
│   └── dashboard.py
├── .env
├── requirements.txt
└── README.md
```

---

## Setup

Clone the repo and install dependencies:

```bash
git clone https://github.com/Purvanshi2204/agentic-financial-research-assistant.git
cd agentic-financial-research-assistant
pip install -r requirements.txt
```

Create a `.env` file and add your API keys:

```
OPENAI_API_KEY=your_key
NEWS_API_KEY=your_key
```

Run the backend:

```bash
uvicorn api.main:app --reload
```

Run the frontend in a new terminal:

```bash
streamlit run frontend/dashboard.py
```

Open `http://localhost:8501` in your browser.

---

## Status

Still in progress — backend agents are being built out. Frontend dashboard is done with mock data and will switch to live data once the API is ready.

- [x] News fetcher agent
- [x] Frontend dashboard
- [x] PDF export
- [x] Keyword alerts
- [x] Company comparison
- [ ] Sentiment agent
- [ ] Market data agent
- [ ] Report writer agent
- [ ] FastAPI endpoint
- [ ] Full integration

---
