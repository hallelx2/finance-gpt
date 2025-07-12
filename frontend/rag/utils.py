import re
from typing import List, Set
from frontend.rag.model import TickerExtractionResult
from decouple import config

# No need for load_dotenv() or os, decouple handles .env automatically

# Common stock tickers and financial terms
COMMON_TICKERS = {
    "AAPL",
    "MSFT",
    "GOOGL",
    "GOOG",
    "AMZN",
    "TSLA",
    "META",
    "NVDA",
    "BRK.A",
    "BRK.B",
    "JPM",
    "JNJ",
    "V",
    "PG",
    "UNH",
    "HD",
    "MA",
    "BAC",
    "ABBV",
    "PFE",
    "KO",
    "AVGO",
    "PEP",
    "TMO",
    "COST",
    "DIS",
    "ABT",
    "DHR",
    "VZ",
    "ADBE",
    "NFLX",
    "XOM",
    "WMT",
    "CRM",
    "LLY",
    "ORCL",
    "ACN",
    "CVX",
    "MRK",
    "QCOM",
    "TXN",
    "AMD",
    "HON",
    "NKE",
    "IBM",
    "INTC",
    "BA",
    "GS",
    "CAT",
    "AMGN",
    "SBUX",
    "INTU",
    "BKNG",
    "ISRG",
}

# Financial keywords that might indicate market discussion
FINANCIAL_KEYWORDS = {
    "stock",
    "stocks",
    "market",
    "trading",
    "investment",
    "portfolio",
    "earnings",
    "revenue",
    "profit",
    "loss",
    "dividend",
    "shares",
    "price",
    "valuation",
    "bull",
    "bear",
    "volatility",
    "analysis",
    "forecast",
    "outlook",
}


def extract_tickers_from_query(query: str) -> TickerExtractionResult:
    """
    Extract stock tickers from a user query using multiple strategies.

    Args:
        query (str): The user's query

    Returns:
        TickerExtractionResult: Extracted tickers with confidence and query type
    """
    query_upper = query.upper()
    found_tickers = set()

    # Strategy 1: Direct ticker matches (high confidence)
    ticker_pattern = r"\b[A-Z]{1,5}\b"
    potential_tickers = re.findall(ticker_pattern, query_upper)

    for ticker in potential_tickers:
        if ticker in COMMON_TICKERS:
            found_tickers.add(ticker)

    # Strategy 2: Company name to ticker mapping (medium confidence)
    company_mappings = {
        "APPLE": "AAPL",
        "MICROSOFT": "MSFT",
        "GOOGLE": "GOOGL",
        "ALPHABET": "GOOGL",
        "AMAZON": "AMZN",
        "TESLA": "TSLA",
        "META": "META",
        "FACEBOOK": "META",
        "NVIDIA": "NVDA",
        "BERKSHIRE": "BRK.A",
        "JPMORGAN": "JPM",
        "JOHNSON": "JNJ",
        "VISA": "V",
        "PROCTER": "PG",
        "GAMBLE": "PG",
        "NETFLIX": "NFLX",
        "DISNEY": "DIS",
        "WALMART": "WMT",
        "COCA": "KO",
        "COLA": "KO",
        "INTEL": "INTC",
        "BOEING": "BA",
        "GOLDMAN": "GS",
        "SACHS": "GS",
        "STARBUCKS": "SBUX",
        "ADOBE": "ADBE",
    }

    for company, ticker in company_mappings.items():
        if company in query_upper:
            found_tickers.add(ticker)

    # Determine query type
    query_type = determine_query_type(query, found_tickers)

    # Calculate confidence
    confidence = calculate_extraction_confidence(query, found_tickers)

    return TickerExtractionResult(
        tickers=list(found_tickers), confidence=confidence, query_type=query_type
    )


def determine_query_type(query: str, tickers: Set[str]) -> str:
    """
    Determine the type of query based on content and extracted tickers.

    Args:
        query (str): The user's query
        tickers (Set[str]): Extracted tickers

    Returns:
        str: Query type classification
    """
    query_lower = query.lower()

    if tickers:
        if len(tickers) == 1:
            return "stock_specific"
        elif len(tickers) > 1:
            return "multi_stock_comparison"

    # Check for market-wide queries
    market_terms = ["market", "economy", "sector", "industry", "overall", "general"]
    if any(term in query_lower for term in market_terms):
        return "market_general"

    # Check for news requests
    news_terms = ["news", "latest", "recent", "update", "announcement"]
    if any(term in query_lower for term in news_terms):
        return "news_request"

    # Check for analysis requests
    analysis_terms = ["analyze", "analysis", "forecast", "predict", "outlook"]
    if any(term in query_lower for term in analysis_terms):
        return "analysis_request"

    # Check for investment advice
    investment_terms = ["invest", "buy", "sell", "portfolio", "recommend"]
    if any(term in query_lower for term in investment_terms):
        return "investment_advice"

    return "general_financial"


def calculate_extraction_confidence(query: str, tickers: Set[str]) -> float:
    """
    Calculate confidence score for ticker extraction.

    Args:
        query (str): The user's query
        tickers (Set[str]): Extracted tickers

    Returns:
        float: Confidence score between 0 and 1
    """
    confidence = 0.0

    # Base confidence from number of tickers found
    if tickers:
        confidence += 0.4

        # Bonus for multiple tickers
        if len(tickers) > 1:
            confidence += 0.2

    # Bonus for financial keywords
    query_lower = query.lower()
    financial_word_count = sum(
        1 for keyword in FINANCIAL_KEYWORDS if keyword in query_lower
    )
    confidence += min(financial_word_count * 0.1, 0.3)

    # Bonus for explicit ticker format (e.g., $AAPL)
    if re.search(r"\$[A-Z]{1,5}\b", query):
        confidence += 0.2

    return min(confidence, 1.0)


def get_default_tickers() -> List[str]:
    """
    Get default tickers to use when no specific tickers are extracted.

    Returns:
        List[str]: List of default popular tickers
    """
    # Optionally allow override from environment using python-decouple
    default_tickers_env = config(
        "DEFAULT_TICKERS", default="AAPL,MSFT,GOOGL,AMZN,TSLA,META,NVDA"
    )
    return [
        ticker.strip() for ticker in default_tickers_env.split(",") if ticker.strip()
    ]


def format_news_for_context(news_items: List[dict]) -> str:
    """
    Format news items into a context string for LLM prompting.

    Args:
        news_items (List[dict]): List of news items

    Returns:
        str: Formatted context string
    """
    if not news_items:
        return "No recent news available."

    context_parts = []
    for i, item in enumerate(news_items[:10], 1):  # Limit to top 10
        context_parts.append(
            f"{i}. {item.get('headline', 'No headline')}\n"
            f"   Summary: {item.get('summary', 'No summary')}\n"
            f"   Ticker: {item.get('ticker', 'N/A')}\n"
            f"   Source: {item.get('source', 'N/A')}\n"
        )

    return "\n".join(context_parts)


def rank_news_by_relevance(
    news_items: List[dict], query: str, tickers: List[str]
) -> List[dict]:
    """
    Rank news items by relevance to the query and tickers.

    Args:
        news_items (List[dict]): List of news items
        query (str): User's query
        tickers (List[str]): Extracted tickers

    Returns:
        List[dict]: Ranked news items
    """
    if not news_items:
        return []

    query_lower = query.lower()
    query_words = set(query_lower.split())

    def calculate_relevance_score(item: dict) -> float:
        score = 0.0

        # Score based on ticker relevance
        item_ticker = item.get("ticker", "").upper()
        if item_ticker in tickers:
            score += 0.5

        # Score based on headline relevance
        headline = item.get("headline", "").lower()
        headline_words = set(headline.split())
        common_words = query_words.intersection(headline_words)
        score += len(common_words) * 0.1

        # Score based on summary relevance
        summary = item.get("summary", "").lower()
        summary_words = set(summary.split())
        common_summary_words = query_words.intersection(summary_words)
        score += len(common_summary_words) * 0.05

        # Bonus for recent news (if datetime is available)
        if "datetime" in item:
            # Add recency bonus (implementation depends on your date format)
            pass

        return score

    # Add relevance scores and sort
    for item in news_items:
        item["relevance_score"] = calculate_relevance_score(item)

    return sorted(news_items, key=lambda x: x.get("relevance_score", 0), reverse=True)
