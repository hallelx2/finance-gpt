"""
Configuration module for Finance GPT Streamlit application.

Contains all application settings, constants, and configuration options.
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AppConfig:
    """Main application configuration."""

    # App metadata
    APP_NAME: str = "Finance GPT"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-Powered Financial Analysis Assistant"

    # Page configuration
    PAGE_TITLE: str = "Finance GPT - AI Financial Assistant"
    PAGE_ICON: str = "📈"
    LAYOUT: str = "wide"
    INITIAL_SIDEBAR_STATE: str = "expanded"

    # UI Configuration
    MAX_CHAT_HISTORY: int = 50
    DEFAULT_THEME: str = "light"
    ANIMATION_DURATION: float = 0.3

    # RAG Pipeline Configuration
    MAX_RETRIEVALS: int = 8
    DEFAULT_TICKERS: List[str] = field(default_factory=lambda: [
        "AAPL",
        "MSFT",
        "GOOGL",
        "AMZN",
        "TSLA",
        "META",
        "NVDA",
    ])
    CONFIDENCE_THRESHOLD: float = 0.3

    # API Configuration
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    FINHUB_API_KEY: str = os.getenv("FINHUB_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

    # Error handling
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0
    TIMEOUT_SECONDS: int = 30

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "finance_gpt_frontend.log"

    def __post_init__(self):
        """Post-initialization setup."""
        if self.DEFAULT_TICKERS is None:
            self.DEFAULT_TICKERS = [
                "AAPL",
                "MSFT",
                "GOOGL",
                "AMZN",
                "TSLA",
                "META",
                "NVDA",
            ]

    def validate_config(self) -> Dict[str, bool]:
        """
        Validate configuration settings.

        Returns:
            Dict[str, bool]: Validation results for each setting
        """
        validation_results = {
            "mongodb_uri": bool(self.MONGODB_URI),
            "finhub_api_key": bool(self.FINHUB_API_KEY),
            "google_api_key": bool(self.GOOGLE_API_KEY),
            "max_retrievals": self.MAX_RETRIEVALS > 0,
            "confidence_threshold": 0.0 <= self.CONFIDENCE_THRESHOLD <= 1.0,
            "max_retries": self.MAX_RETRIES > 0,
            "timeout": self.TIMEOUT_SECONDS > 0,
        }

        return validation_results

    def get_missing_config(self) -> List[str]:
        """
        Get list of missing or invalid configuration items.

        Returns:
            List[str]: List of missing configuration keys
        """
        validation = self.validate_config()
        return [key for key, is_valid in validation.items() if not is_valid]


# UI Constants
class UIConstants:
    """UI-related constants and styling."""

    # Colors
    PRIMARY_COLOR = "#1f77b4"
    SECONDARY_COLOR = "#ff7f0e"
    SUCCESS_COLOR = "#2ca02c"
    WARNING_COLOR = "#ff7f0e"
    ERROR_COLOR = "#d62728"

    # Sentiment colors
    POSITIVE_COLOR = "#2ca02c"
    NEGATIVE_COLOR = "#d62728"
    NEUTRAL_COLOR = "#7f7f7f"

    # Icons
    ICONS = {
        "user": "👤",
        "assistant": "🤖",
        "loading": "⏳",
        "error": "❌",
        "success": "✅",
        "warning": "⚠️",
        "info": "ℹ️",
        "stocks": "📊",
        "sentiment_positive": "📈",
        "sentiment_negative": "📉",
        "sentiment_neutral": "➡️",
        "news": "📰",
        "insights": "💡",
        "confidence": "🎯",
        "outlook": "🔮",
    }

    # Message styling
    USER_MESSAGE_STYLE = """
    <div style="
        background-color: #e3f2fd;
        padding: 10px 15px;
        border-radius: 10px;
        margin: 5px 0;
        border-left: 4px solid #1f77b4;
    ">
        <strong>You:</strong> {message}
    </div>
    """

    ASSISTANT_MESSAGE_STYLE = """
    <div style="
        background-color: #f5f5f5;
        padding: 10px 15px;
        border-radius: 10px;
        margin: 5px 0;
        border-left: 4px solid #2ca02c;
    ">
        <strong>Finance GPT:</strong> {message}
    </div>
    """

    ERROR_MESSAGE_STYLE = """
    <div style="
        background-color: #ffebee;
        padding: 10px 15px;
        border-radius: 10px;
        margin: 5px 0;
        border-left: 4px solid #d62728;
    ">
        <strong>Error:</strong> {message}
    </div>
    """


# UI Configuration (for use as UIConfig)
class UIConfig:
    """UI configuration for colors, styles, and theming."""

    # Main theme colors
    PRIMARY_COLOR = UIConstants.PRIMARY_COLOR
    SECONDARY_COLOR = UIConstants.SECONDARY_COLOR
    SUCCESS_COLOR = UIConstants.SUCCESS_COLOR
    WARNING_COLOR = UIConstants.WARNING_COLOR
    ERROR_COLOR = UIConstants.ERROR_COLOR
    ACCENT_COLOR = UIConstants.PRIMARY_COLOR

    # Message bubble colors
    USER_MESSAGE_COLOR = "#e3f2fd"
    ASSISTANT_MESSAGE_COLOR = "#f5f5f5"
    SYSTEM_MESSAGE_COLOR = "#fffde7"

    # Other UI settings
    BORDER_RADIUS = 10
    FONT_FAMILY = "'Segoe UI', 'Roboto', 'Arial', sans-serif"
    FONT_SIZE = 16
    MAX_WIDTH = 900
    MIN_WIDTH = 320
    PADDING = 16
    ANIMATION_DURATION = 0.3

    # For compatibility with code expecting UIConfig
    ICONS = UIConstants.ICONS
    POSITIVE_COLOR = UIConstants.POSITIVE_COLOR
    NEGATIVE_COLOR = UIConstants.NEGATIVE_COLOR
    NEUTRAL_COLOR = UIConstants.NEUTRAL_COLOR


# Sample data for testing
class SampleData:
    """Sample data for testing and development."""

    SAMPLE_QUESTIONS = [
        "What's the latest news about Apple (AAPL)?",
        "How is Tesla performing in the market?",
        "What's the market sentiment for tech stocks?",
        "Should I invest in Microsoft or Google?",
        "What are the key insights for the financial market today?",
        "How is the overall market performing?",
        "What's the outlook for renewable energy stocks?",
        "Tell me about recent developments in the banking sector.",
    ]

    SAMPLE_TICKERS = [
        "AAPL",
        "MSFT",
        "GOOGL",
        "AMZN",
        "TSLA",
        "META",
        "NVDA",
        "NFLX",
        "JPM",
        "BAC",
        "WMT",
        "DIS",
        "V",
        "MA",
        "PG",
        "JNJ",
        "UNH",
        "HD",
    ]


# Create global config instance
config = AppConfig()

# Validate configuration on import
if __name__ == "__main__":
    print("Configuration validation:")
    validation = config.validate_config()
    for key, is_valid in validation.items():
        status = "✅" if is_valid else "❌"
        print(f"{status} {key}: {is_valid}")

    missing = config.get_missing_config()
    if missing:
        print(f"\nMissing configuration: {missing}")
    else:
        print("\n✅ All configuration is valid!")
