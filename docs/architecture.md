# System Architecture

## Overview
The Agentic Financial Research Assistant is a multi-agent AI system that autonomously collects financial news and market data to generate structured company insight reports.

## Architecture Components

### 1. News Agent
- Collects latest financial news using NewsAPI
- Filters relevant articles

### 2. Market Data Agent
- Fetches stock data using Yahoo Finance
- Retrieves price, volume, and trend indicators

### 3. Sentiment Agent
- Uses LLM APIs to analyze sentiment of financial news
- Extracts positive, neutral, or negative signals

### 4. Report Agent
- Aggregates all data
- Generates structured company research reports

## Workflow

User Request  
→ LangGraph Workflow  
→ News Agent  
→ Market Data Agent  
→ Sentiment Analysis  
→ Report Generation