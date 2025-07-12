from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any


# Define the Model Sxhema to store the documents in MongoD
class DocumentModel(BaseModel):
    category: str
    datetime: int
    headline: str
    id: int
    image: Optional[str] = None
    related: str
    source: str
    summary: str
    url: str
    ticker: str
    date: str

    class Config:
        from_attributes = True


# Structured output models for LLM responses
class NewsItem(BaseModel):
    """Individual news item with key information"""

    headline: str
    summary: str
    ticker: str
    source: str
    relevance_score: Optional[float] = None
    date: Optional[str] = None


class FinancialAnswer(BaseModel):
    """Structured output for financial Q&A responses"""

    summary: str  # Main answer to the user's question
    key_insights: List[str]  # List of key insights or bullet points
    top_news: List[NewsItem]  # Most relevant news articles
    mentioned_tickers: List[str]  # Stock tickers mentioned in the analysis
    sentiment: Optional[str] = None  # Overall sentiment: positive/negative/neutral
    confidence_score: Optional[float] = None  # Confidence in the analysis (0-1)
    market_outlook: Optional[str] = None  # Brief market outlook if relevant


class TickerExtractionResult(BaseModel):
    """Result of ticker extraction from user query"""

    tickers: List[str]  # Extracted stock tickers
    confidence: float  # Confidence in extraction (0-1)
    query_type: (
        str  # Type of query: "stock_specific", "market_general", "news_request", etc.
    )
