import logging
import traceback
import time
from typing import Optional, Any, Callable, Dict, List
from functools import wraps
from frontend.rag.model import FinancialAnswer, NewsItem
from rich import print
from decouple import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("finance_gpt.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


class FinanceGPTError(Exception):
    """Base exception for Finance GPT application."""

    pass


class TickerExtractionError(FinanceGPTError):
    """Error in ticker extraction process."""

    pass


class FinnhubAPIError(FinanceGPTError):
    """Error with Finnhub API calls."""

    pass


class VectorStoreError(FinanceGPTError):
    """Error with vector store operations."""

    pass


class LLMError(FinanceGPTError):
    """Error with LLM operations."""

    pass


class MongoDBError(FinanceGPTError):
    """Error with MongoDB operations."""

    pass


def retry_on_failure(
    max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0
):
    """
    Decorator to retry functions on failure with exponential backoff.

    Args:
        max_retries (int): Maximum number of retry attempts
        delay (float): Initial delay between retries in seconds
        backoff_factor (float): Factor to multiply delay by after each retry
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}"
                        )
                        logger.info(f"Retrying in {current_delay} seconds...")
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}"
                        )
                        break

            raise last_exception

        return wrapper

    return decorator


def safe_execute(
    func: Callable, default_return: Any = None, error_message: str = "Operation failed"
) -> Any:
    """
    Safely execute a function with error handling.

    Args:
        func (Callable): Function to execute
        default_return (Any): Default value to return on error
        error_message (str): Custom error message

    Returns:
        Any: Function result or default value
    """
    try:
        return func()
    except Exception as e:
        logger.error(f"{error_message}: {str(e)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return default_return


def validate_environment_variables() -> Dict[str, bool]:
    """
    Validate that all required environment variables are set.

    Returns:
        Dict[str, bool]: Dictionary of variable names and their availability
    """
    required_vars = [
        "MONGODB_URI",
        "FINHUB_API_KEY",
        "GOOGLE_API_KEY",  # For Google Generative AI
    ]

    results = {}
    missing_vars = []

    for var in required_vars:
        is_set = bool(config(var, default=None))
        results[var] = is_set
        if not is_set:
            missing_vars.append(var)

    if missing_vars:
        logger.error(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
        raise FinanceGPTError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    logger.info("All required environment variables are set")
    return results


def create_fallback_response(query: str, error: Exception) -> FinancialAnswer:
    """
    Create a fallback structured response when the main pipeline fails.

    Args:
        query (str): Original user query
        error (Exception): The error that occurred

    Returns:
        FinancialAnswer: Fallback structured response
    """
    error_type = type(error).__name__

    # Determine appropriate fallback message based on error type
    if isinstance(error, FinnhubAPIError):
        summary = "I'm currently unable to fetch the latest financial data from external sources. Please try again in a few minutes."
        insights = ["External financial data service is temporarily unavailable"]
    elif isinstance(error, VectorStoreError):
        summary = "I'm experiencing issues with my knowledge base. I can provide general information but may not have the latest updates."
        insights = [
            "Knowledge base temporarily unavailable",
            "Consider asking about general financial concepts",
        ]
    elif isinstance(error, LLMError):
        summary = "I'm having trouble processing your request right now. Please try rephrasing your question or try again later."
        insights = [
            "Language model temporarily unavailable",
            "Try asking simpler questions",
        ]
    elif isinstance(error, MongoDBError):
        summary = "I'm experiencing database connectivity issues. Some features may be limited."
        insights = ["Database connection issues", "Historical data may be unavailable"]
    else:
        summary = f"I encountered an unexpected error while processing your request: {str(error)}"
        insights = [
            "Unexpected system error occurred",
            "Please try again or contact support",
        ]

    return FinancialAnswer(
        summary=summary,
        key_insights=insights,
        top_news=[],
        mentioned_tickers=[],
        sentiment="neutral",
        confidence_score=0.0,
        market_outlook="Unable to provide outlook due to system error",
    )


def log_user_interaction(
    query: str,
    response: FinancialAnswer,
    processing_time: float,
    error: Optional[Exception] = None,
):
    """
    Log user interaction for monitoring and debugging.

    Args:
        query (str): User query
        response (FinancialAnswer): System response
        processing_time (float): Time taken to process the request
        error (Optional[Exception]): Any error that occurred
    """
    log_data = {
        "query": query,
        "processing_time": processing_time,
        "response_confidence": response.confidence_score,
        "mentioned_tickers": response.mentioned_tickers,
        "sentiment": response.sentiment,
        "news_count": len(response.top_news),
        "insights_count": len(response.key_insights),
        "error": str(error) if error else None,
    }

    if error:
        logger.error(f"User interaction failed: {log_data}")
    else:
        logger.info(f"User interaction completed: {log_data}")


def validate_ticker_list(tickers: List[str]) -> List[str]:
    """
    Validate and clean ticker list.

    Args:
        tickers (List[str]): List of ticker symbols

    Returns:
        List[str]: Validated ticker list
    """
    if not tickers:
        logger.warning("Empty ticker list provided")
        return []

    # Remove duplicates and invalid tickers
    valid_tickers = []
    for ticker in tickers:
        if isinstance(ticker, str) and ticker.strip():
            cleaned_ticker = ticker.strip().upper()
            if len(cleaned_ticker) <= 5 and cleaned_ticker.isalpha():
                valid_tickers.append(cleaned_ticker)
            else:
                logger.warning(f"Invalid ticker format: {ticker}")
        else:
            logger.warning(f"Invalid ticker type: {ticker}")

    # Remove duplicates while preserving order
    unique_tickers = list(dict.fromkeys(valid_tickers))

    if len(unique_tickers) != len(tickers):
        logger.info(f"Cleaned ticker list: {tickers} -> {unique_tickers}")

    return unique_tickers


def check_system_health() -> Dict[str, bool]:
    """
    Check system health for all components.

    Returns:
        Dict[str, bool]: Health status for each component
    """
    health_status = {
        "environment_variables": False,
        "mongodb_connection": False,
        "vector_store": False,
        "llm_connection": False,
    }

    # Check environment variables
    try:
        validate_environment_variables()
        health_status["environment_variables"] = True
    except Exception as e:
        logger.error(f"Environment variables check failed: {e}")

    # Check MongoDB connection
    try:
        from frontend.rag.vector_search import get_mongo_collection

        collection = get_mongo_collection("health_check")
        collection.find_one()  # Simple query to test connection
        health_status["mongodb_connection"] = True
    except Exception as e:
        logger.error(f"MongoDB connection check failed: {e}")

    # Check vector store
    try:
        from frontend.rag.vector_search import initialize_vector_store

        vector_store = initialize_vector_store()
        health_status["vector_store"] = True
    except Exception as e:
        logger.error(f"Vector store check failed: {e}")

    # Check LLM connection
    try:
        from frontend.rag.llm_chain import llm

        # Simple test query
        test_response = llm.invoke("Test connection")
        health_status["llm_connection"] = True
    except Exception as e:
        logger.error(f"LLM connection check failed: {e}")

    overall_health = all(health_status.values())
    logger.info(f"System health check: {health_status} (Overall: {overall_health})")

    return health_status


def format_error_for_user(error: Exception) -> str:
    """
    Format error message for user display.

    Args:
        error (Exception): The error to format

    Returns:
        str: User-friendly error message
    """
    error_messages = {
        FinnhubAPIError: "I'm having trouble accessing financial data right now. Please try again in a few minutes.",
        VectorStoreError: "I'm experiencing issues with my knowledge base. Please try again later.",
        LLMError: "I'm having trouble processing your request. Please try rephrasing your question.",
        MongoDBError: "I'm experiencing database issues. Some features may be limited.",
        TickerExtractionError: "I had trouble understanding which stocks you're asking about. Please be more specific.",
    }

    error_type = type(error)
    return error_messages.get(
        error_type, "I encountered an unexpected error. Please try again."
    )


# Initialize system health check on import
if __name__ == "__main__":
    print("Running system health check...")
    health = check_system_health()
    print(f"System health: {health}")
else:
    # Run a quick health check when module is imported
    safe_execute(
        lambda: check_system_health(),
        default_return={"system": False},
        error_message="Initial system health check failed",
    )
