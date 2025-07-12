"""
State management module for Finance GPT Streamlit application.

Handles chat history, user sessions, and application state management.
"""

import streamlit as st
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

from .config import config, UIConstants

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """Represents a single chat message."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    role: str = "user"  # 'user' or 'assistant'
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        """Create message from dictionary."""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class AnalysisResult:
    """Represents the result of a financial analysis."""

    summary: str = ""
    key_insights: List[str] = field(default_factory=list)
    mentioned_tickers: List[str] = field(default_factory=list)
    sentiment: str = "neutral"
    confidence_score: float = 0.0
    market_outlook: Optional[str] = None
    top_news: List[Dict[str, Any]] = field(default_factory=list)
    processing_time: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis result to dictionary."""
        return {
            "summary": self.summary,
            "key_insights": self.key_insights,
            "mentioned_tickers": self.mentioned_tickers,
            "sentiment": self.sentiment,
            "confidence_score": self.confidence_score,
            "market_outlook": self.market_outlook,
            "top_news": self.top_news,
            "processing_time": self.processing_time,
            "error": self.error,
        }


class StateManager:
    """Manages application state for the Streamlit app."""

    def __init__(self):
        """Initialize state manager."""
        self.session_id = self._get_or_create_session_id()
        self._initialize_session_state()

    def _get_or_create_session_id(self) -> str:
        """Get or create a unique session ID."""
        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        return st.session_state.session_id

    def _initialize_session_state(self):
        """Initialize session state variables."""
        defaults = {
            "chat_history": [],
            "current_analysis": None,
            "is_processing": False,
            "current_tickers": [],
            "current_sentiment": "neutral",
            "confidence_score": 0.0,
            "error_message": None,
            "last_query_time": None,
            "total_queries": 0,
            "session_start_time": datetime.now(),
            "ui_settings": {
                "theme": config.DEFAULT_THEME,
                "show_advanced_info": False,
                "auto_scroll": True,
            },
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    # Chat History Management
    def add_message(
        self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a message to chat history.

        Args:
            role (str): Message role ('user' or 'assistant')
            content (str): Message content
            metadata (Optional[Dict]): Additional metadata

        Returns:
            str: Message ID
        """
        message = ChatMessage(role=role, content=content, metadata=metadata or {})

        st.session_state.chat_history.append(message)

        # Limit chat history size
        if len(st.session_state.chat_history) > config.MAX_CHAT_HISTORY:
            st.session_state.chat_history = st.session_state.chat_history[
                -config.MAX_CHAT_HISTORY :
            ]

        logger.info(f"Added {role} message: {message.id}")
        return message.id

    def get_chat_history(self) -> List[ChatMessage]:
        """Get chat history."""
        return st.session_state.chat_history

    def clear_chat_history(self):
        """Clear chat history."""
        st.session_state.chat_history = []
        st.session_state.current_analysis = None
        st.session_state.current_tickers = []
        st.session_state.current_sentiment = "neutral"
        st.session_state.confidence_score = 0.0
        st.session_state.error_message = None
        logger.info("Chat history cleared")

    def get_last_message(self, role: Optional[str] = None) -> Optional[ChatMessage]:
        """
        Get the last message, optionally filtered by role.

        Args:
            role (Optional[str]): Filter by role

        Returns:
            Optional[ChatMessage]: Last message or None
        """
        history = self.get_chat_history()
        if not history:
            return None

        if role:
            for message in reversed(history):
                if message.role == role:
                    return message
            return None

        return history[-1]

    # Processing State Management
    def set_processing(self, is_processing: bool):
        """Set processing state."""
        st.session_state.is_processing = is_processing
        if is_processing:
            st.session_state.last_query_time = datetime.now()

    def is_processing(self) -> bool:
        """Check if currently processing."""
        return st.session_state.is_processing

    # Analysis Results Management
    def set_analysis_result(self, result: AnalysisResult):
        """Set the current analysis result."""
        st.session_state.current_analysis = result
        st.session_state.current_tickers = result.mentioned_tickers
        st.session_state.current_sentiment = result.sentiment
        st.session_state.confidence_score = result.confidence_score
        st.session_state.total_queries += 1

        logger.info(
            f"Analysis result set: {len(result.mentioned_tickers)} tickers, {result.sentiment} sentiment"
        )

    def get_analysis_result(self) -> Optional[AnalysisResult]:
        """Get the current analysis result."""
        return st.session_state.current_analysis

    def get_current_tickers(self) -> List[str]:
        """Get currently analyzed tickers."""
        return st.session_state.current_tickers

    def get_current_sentiment(self) -> str:
        """Get current sentiment."""
        return st.session_state.current_sentiment

    def get_confidence_score(self) -> float:
        """Get current confidence score."""
        return st.session_state.confidence_score

    # Error Management
    def set_error(self, error_message: str):
        """Set error message."""
        st.session_state.error_message = error_message
        logger.error(f"Error set: {error_message}")

    def get_error(self) -> Optional[str]:
        """Get current error message."""
        return st.session_state.error_message

    def clear_error(self):
        """Clear error message."""
        st.session_state.error_message = None

    # UI Settings Management
    def get_ui_setting(self, key: str, default: Any = None) -> Any:
        """Get UI setting value."""
        return st.session_state.ui_settings.get(key, default)

    def set_ui_setting(self, key: str, value: Any):
        """Set UI setting value."""
        st.session_state.ui_settings[key] = value

    def toggle_ui_setting(self, key: str) -> bool:
        """Toggle boolean UI setting."""
        current = self.get_ui_setting(key, False)
        self.set_ui_setting(key, not current)
        return not current

    # Session Statistics
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        session_duration = datetime.now() - st.session_state.session_start_time

        return {
            "session_id": self.session_id,
            "session_duration": str(session_duration),
            "total_messages": len(st.session_state.chat_history),
            "total_queries": st.session_state.total_queries,
            "last_query_time": st.session_state.last_query_time,
            "current_tickers": st.session_state.current_tickers,
            "current_sentiment": st.session_state.current_sentiment,
            "confidence_score": st.session_state.confidence_score,
        }

    # Data Export/Import
    def export_session_data(self) -> Dict[str, Any]:
        """Export session data for backup or analysis."""
        return {
            "session_id": self.session_id,
            "chat_history": [msg.to_dict() for msg in st.session_state.chat_history],
            "current_analysis": (
                st.session_state.current_analysis.to_dict()
                if st.session_state.current_analysis
                else None
            ),
            "session_stats": self.get_session_stats(),
            "ui_settings": st.session_state.ui_settings,
            "export_timestamp": datetime.now().isoformat(),
        }

    def import_session_data(self, data: Dict[str, Any]):
        """Import session data from backup."""
        try:
            if "chat_history" in data:
                st.session_state.chat_history = [
                    ChatMessage.from_dict(msg_data) for msg_data in data["chat_history"]
                ]

            if "current_analysis" in data and data["current_analysis"]:
                st.session_state.current_analysis = AnalysisResult(
                    **data["current_analysis"]
                )

            if "ui_settings" in data:
                st.session_state.ui_settings.update(data["ui_settings"])

            logger.info("Session data imported successfully")

        except Exception as e:
            logger.error(f"Failed to import session data: {e}")
            raise

    # Utility Methods
    def format_ticker_display(self) -> str:
        """Format tickers for display."""
        tickers = self.get_current_tickers()
        if not tickers:
            return "No specific stocks analyzed"
        return ", ".join(tickers)

    def get_sentiment_emoji(self) -> str:
        """Get emoji for current sentiment."""
        sentiment = self.get_current_sentiment()
        return UIConstants.ICONS.get(
            f"sentiment_{sentiment}", UIConstants.ICONS["sentiment_neutral"]
        )

    def get_confidence_percentage(self) -> int:
        """Get confidence as percentage."""
        return int(self.get_confidence_score() * 100)

    def can_submit_query(self) -> bool:
        """Check if user can submit a new query."""
        if self.is_processing():
            return False

        # Rate limiting: allow one query per 2 seconds
        if st.session_state.last_query_time:
            time_since_last = datetime.now() - st.session_state.last_query_time
            if time_since_last < timedelta(seconds=2):
                return False

        return True

    def get_rate_limit_remaining(self) -> float:
        """Get remaining time for rate limit."""
        if not st.session_state.last_query_time:
            return 0.0

        time_since_last = datetime.now() - st.session_state.last_query_time
        remaining = max(0, 2.0 - time_since_last.total_seconds())
        return remaining


# Global state manager instance
state_manager = StateManager()
