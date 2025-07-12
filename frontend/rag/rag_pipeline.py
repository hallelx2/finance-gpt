"""
RAGPipeline class for Finance GPT

Wraps the core RAG logic and exposes a process_query method for the frontend.
"""

from frontend.rag.llm_chain import retrieve_and_generate_response
from frontend.rag.model import FinancialAnswer
from frontend.rag.error_handling import create_fallback_response, log_user_interaction


class RAGPipeline:
    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        include_news: bool = True,
        max_results: int = 5,
        analysis_depth: str = "Standard",
    ):
        self.model = model
        self.include_news = include_news
        self.max_results = max_results
        self.analysis_depth = analysis_depth

    def process_query(
        self,
        query: str,
        model: str = None,
        include_news: bool = None,
        max_results: int = None,
        analysis_depth: str = None,
    ):
        """
        Process a user query and return a structured response dict for the frontend.
        """
        # Use provided config or fall back to instance config
        model = model or self.model
        include_news = include_news if include_news is not None else self.include_news
        max_results = max_results or self.max_results
        analysis_depth = analysis_depth or self.analysis_depth

        try:
            # Call the core RAG function
            result = retrieve_and_generate_response(query, num_retrievals=max_results)

            # Convert FinancialAnswer to dict if needed
            if isinstance(result, FinancialAnswer):
                # Convert NewsItem objects to dicts for serialization
                news = [item.dict() for item in getattr(result, "top_news", [])]
                response = {
                    "summary": result.summary,
                    "key_insights": result.key_insights,
                    "mentioned_tickers": result.mentioned_tickers,
                    "sentiment": result.sentiment,
                    "confidence_score": result.confidence_score,
                    "related_news": news,
                    "sources": [],  # Add sources if available in your pipeline
                }
                log_user_interaction(
                    query, result, processing_time=0
                )  # You can add timing if needed
                return response
            elif isinstance(result, dict):
                return result
            else:
                return {
                    "summary": str(result),
                    "key_insights": [],
                    "mentioned_tickers": [],
                    "sentiment": "neutral",
                    "confidence_score": 0.0,
                    "related_news": [],
                    "sources": [],
                }
        except Exception as e:
            fallback = create_fallback_response(query, e)
            return {
                "summary": fallback.summary,
                "key_insights": fallback.key_insights,
                "mentioned_tickers": fallback.mentioned_tickers,
                "sentiment": fallback.sentiment,
                "confidence_score": fallback.confidence_score,
                "related_news": [],
                "sources": [],
            }
