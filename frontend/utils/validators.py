"""
Input validation utilities for Finance GPT Streamlit application.

Contains validation functions for user inputs, data integrity checks, and form validation.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from frontend.core.config import SampleData


class InputValidator:
    """Collection of input validation methods."""

    @staticmethod
    def validate_query(query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate user query input.

        Args:
            query (str): User input query

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not query or not query.strip():
            return False, "Please enter a question about financial markets or stocks."

        # Check minimum length
        if len(query.strip()) < 3:
            return False, "Question is too short. Please provide more details."

        # Check maximum length
        if len(query.strip()) > 1000:
            return False, "Question is too long. Please keep it under 1000 characters."

        # Check for potentially harmful content
        harmful_patterns = [
            r"<script",
            r"javascript:",
            r"<iframe",
            r"<object",
            r"<embed",
        ]

        query_lower = query.lower()
        for pattern in harmful_patterns:
            if re.search(pattern, query_lower):
                return False, "Invalid characters detected in the query."

        return True, None

    @staticmethod
    def validate_ticker_list(
        tickers: List[str],
    ) -> Tuple[bool, Optional[str], List[str]]:
        """
        Validate list of stock tickers.

        Args:
            tickers (List[str]): List of ticker symbols

        Returns:
            Tuple[bool, Optional[str], List[str]]: (is_valid, error_message, cleaned_tickers)
        """
        if not tickers:
            return True, None, []

        cleaned_tickers = []
        invalid_tickers = []

        for ticker in tickers:
            if not isinstance(ticker, str):
                invalid_tickers.append(str(ticker))
                continue

            # Clean and validate ticker format
            cleaned_ticker = ticker.strip().upper()

            # Check ticker format (1-5 alphabetic characters)
            if not re.match(r"^[A-Z]{1,5}$", cleaned_ticker):
                invalid_tickers.append(ticker)
                continue

            # Check against known valid tickers (optional)
            if cleaned_ticker in SampleData.SAMPLE_TICKERS or len(cleaned_ticker) <= 5:
                cleaned_tickers.append(cleaned_ticker)
            else:
                invalid_tickers.append(ticker)

        # Remove duplicates while preserving order
        cleaned_tickers = list(dict.fromkeys(cleaned_tickers))

        if invalid_tickers:
            return (
                False,
                f"Invalid ticker symbols: {', '.join(invalid_tickers)}",
                cleaned_tickers,
            )

        if len(cleaned_tickers) > 10:
            return (
                False,
                "Too many tickers. Please limit to 10 or fewer.",
                cleaned_tickers[:10],
            )

        return True, None, cleaned_tickers

    @staticmethod
    def validate_confidence_score(confidence: float) -> Tuple[bool, Optional[str]]:
        """
        Validate confidence score.

        Args:
            confidence (float): Confidence score

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not isinstance(confidence, (int, float)):
            return False, "Confidence score must be a number."

        if confidence < 0.0 or confidence > 1.0:
            return False, "Confidence score must be between 0.0 and 1.0."

        return True, None

    @staticmethod
    def validate_sentiment(sentiment: str) -> Tuple[bool, Optional[str]]:
        """
        Validate sentiment value.

        Args:
            sentiment (str): Sentiment value

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        valid_sentiments = ["positive", "negative", "neutral"]

        if not isinstance(sentiment, str):
            return False, "Sentiment must be a string."

        if sentiment.lower() not in valid_sentiments:
            return False, f"Sentiment must be one of: {', '.join(valid_sentiments)}"

        return True, None

    @staticmethod
    def validate_analysis_result(result: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate analysis result structure.

        Args:
            result (Dict[str, Any]): Analysis result dictionary

        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        required_fields = [
            "summary",
            "key_insights",
            "mentioned_tickers",
            "sentiment",
            "confidence_score",
        ]

        # Check required fields
        for field in required_fields:
            if field not in result:
                errors.append(f"Missing required field: {field}")

        # Validate individual fields
        if "summary" in result:
            if not isinstance(result["summary"], str) or not result["summary"].strip():
                errors.append("Summary must be a non-empty string.")

        if "key_insights" in result:
            if not isinstance(result["key_insights"], list):
                errors.append("Key insights must be a list.")
            elif len(result["key_insights"]) > 10:
                errors.append("Too many key insights (max 10).")

        if "mentioned_tickers" in result:
            is_valid, error, _ = InputValidator.validate_ticker_list(
                result["mentioned_tickers"]
            )
            if not is_valid:
                errors.append(f"Invalid tickers: {error}")

        if "sentiment" in result:
            is_valid, error = InputValidator.validate_sentiment(result["sentiment"])
            if not is_valid:
                errors.append(f"Invalid sentiment: {error}")

        if "confidence_score" in result:
            is_valid, error = InputValidator.validate_confidence_score(
                result["confidence_score"]
            )
            if not is_valid:
                errors.append(f"Invalid confidence score: {error}")

        return len(errors) == 0, errors

    @staticmethod
    def sanitize_input(input_text: str) -> str:
        """
        Sanitize user input for safe display.

        Args:
            input_text (str): Raw user input

        Returns:
            str: Sanitized input
        """
        if not isinstance(input_text, str):
            return str(input_text)

        # Remove potential HTML/script tags
        sanitized = re.sub(r"<[^>]*>", "", input_text)

        # Remove excessive whitespace
        sanitized = re.sub(r"\s+", " ", sanitized).strip()

        # Limit length
        if len(sanitized) > 2000:
            sanitized = sanitized[:2000] + "..."

        return sanitized

    @staticmethod
    def validate_date_range(
        start_date: datetime, end_date: datetime
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate date range.

        Args:
            start_date (datetime): Start date
            end_date (datetime): End date

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            return False, "Dates must be datetime objects."

        if start_date > end_date:
            return False, "Start date must be before end date."

        # Check if dates are too far in the future
        now = datetime.now()
        if start_date > now or end_date > now:
            return False, "Dates cannot be in the future."

        # Check if date range is too large (more than 1 year)
        if (end_date - start_date).days > 365:
            return False, "Date range cannot exceed 1 year."

        return True, None

    @staticmethod
    def validate_session_data(session_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate session data structure.

        Args:
            session_data (Dict[str, Any]): Session data dictionary

        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        required_fields = ["session_id", "chat_history"]

        # Check required fields
        for field in required_fields:
            if field not in session_data:
                errors.append(f"Missing required field: {field}")

        # Validate session_id
        if "session_id" in session_data:
            if (
                not isinstance(session_data["session_id"], str)
                or not session_data["session_id"].strip()
            ):
                errors.append("Session ID must be a non-empty string.")

        # Validate chat_history
        if "chat_history" in session_data:
            if not isinstance(session_data["chat_history"], list):
                errors.append("Chat history must be a list.")
            else:
                for i, message in enumerate(session_data["chat_history"]):
                    if not isinstance(message, dict):
                        errors.append(f"Chat message {i} must be a dictionary.")
                        continue

                    required_msg_fields = ["role", "content", "timestamp"]
                    for field in required_msg_fields:
                        if field not in message:
                            errors.append(f"Chat message {i} missing field: {field}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_file_upload(
        file_content: str, max_size_mb: float = 5.0
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file content.

        Args:
            file_content (str): File content as string
            max_size_mb (float): Maximum file size in MB

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not isinstance(file_content, str):
            return False, "File content must be a string."

        # Check file size
        file_size_mb = len(file_content.encode("utf-8")) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            return (
                False,
                f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({max_size_mb}MB).",
            )

        # Check for potentially harmful content
        harmful_patterns = [
            r"<script",
            r"javascript:",
            r"<iframe",
            r"<object",
            r"<embed",
            r"eval\(",
            r"exec\(",
        ]

        content_lower = file_content.lower()
        for pattern in harmful_patterns:
            if re.search(pattern, content_lower):
                return False, "File contains potentially harmful content."

        return True, None

    @staticmethod
    def validate_api_response(response: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate API response structure.

        Args:
            response (Dict[str, Any]): API response dictionary

        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []

        if not isinstance(response, dict):
            errors.append("Response must be a dictionary.")
            return False, errors

        # Check for error field
        if "error" in response:
            if response["error"]:
                errors.append(f"API returned error: {response['error']}")

        # Check for required success fields
        if "error" not in response or not response["error"]:
            if "data" not in response:
                errors.append("Response missing 'data' field.")

        return len(errors) == 0, errors

    @staticmethod
    def is_safe_url(url: str) -> bool:
        """
        Check if URL is safe for display/linking.

        Args:
            url (str): URL to validate

        Returns:
            bool: True if URL is safe
        """
        if not isinstance(url, str):
            return False

        # Check for valid HTTP/HTTPS URLs
        if not re.match(r"^https?://", url):
            return False

        # Check for potentially harmful schemes
        harmful_schemes = ["javascript:", "data:", "vbscript:", "file:"]
        url_lower = url.lower()

        for scheme in harmful_schemes:
            if scheme in url_lower:
                return False

        return True
