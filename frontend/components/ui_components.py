"""
Reusable UI components for Finance GPT Streamlit application.

Contains modular components for chat interface, status displays, and interactive elements.
"""

import streamlit as st
import sys
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from frontend.core.state_manager import ChatMessage, AnalysisResult
from frontend.utils.formatters import MessageFormatter, DataFormatter
from frontend.utils.ui_helpers import UIHelpers
from frontend.core.config import UIConfig


class MessageComponent:
    """Component for displaying chat messages."""

    @staticmethod
    def display_message(message: ChatMessage, show_timestamp: bool = True) -> None:
        """
        Display a single chat message.

        Args:
            message (ChatMessage): Message to display
            show_timestamp (bool): Whether to show timestamp
        """
        # Determine message styling based on role
        if message.role == "user":
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col2:
                    st.markdown(
                        f"""
                        <div style="background-color: {UIConfig.USER_MESSAGE_COLOR};
                                   padding: 10px; border-radius: 10px; margin: 5px 0;">
                            <strong>You:</strong> {message.content}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if show_timestamp:
                        st.caption(
                            f"🕒 {message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
                        )

        elif message.role == "assistant":
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(
                        f"""
                        <div style="background-color: {UIConfig.ASSISTANT_MESSAGE_COLOR};
                                   padding: 10px; border-radius: 10px; margin: 5px 0;">
                            <strong>Finance GPT:</strong> {message.content}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if show_timestamp:
                        st.caption(
                            f"🤖 {message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
                        )

        elif message.role == "system":
            st.info(f"ℹ️ {message.content}")

    @staticmethod
    def display_message_list(
        messages: List[ChatMessage], max_messages: Optional[int] = None
    ) -> None:
        """
        Display a list of chat messages.

        Args:
            messages (List[ChatMessage]): List of messages to display
            max_messages (Optional[int]): Maximum number of messages to show
        """
        if not messages:
            st.info("No messages yet. Start a conversation!")
            return

        # Limit messages if specified
        display_messages = messages[-max_messages:] if max_messages else messages

        for message in display_messages:
            MessageComponent.display_message(message)
            st.markdown("---")


class StatusComponent:
    """Component for displaying status indicators."""

    @staticmethod
    def show_loading(message: str = "Processing...") -> None:
        """Show loading indicator with message."""
        with st.spinner(message):
            st.empty()

    @staticmethod
    def show_success(message: str) -> None:
        """Show success message."""
        st.success(f"✅ {message}")

    @staticmethod
    def show_error(message: str, details: Optional[str] = None) -> None:
        """Show error message with optional details."""
        st.error(f"❌ {message}")
        if details:
            with st.expander("Error Details"):
                st.code(details)

    @staticmethod
    def show_warning(message: str) -> None:
        """Show warning message."""
        st.warning(f"⚠️ {message}")

    @staticmethod
    def show_info(message: str) -> None:
        """Show info message."""
        st.info(f"ℹ️ {message}")

    @staticmethod
    def show_processing_status(step: str, total_steps: int, current_step: int) -> None:
        """
        Show processing progress.

        Args:
            step (str): Current step description
            total_steps (int): Total number of steps
            current_step (int): Current step number
        """
        progress = current_step / total_steps
        st.progress(progress)
        st.caption(f"Step {current_step}/{total_steps}: {step}")


class AnalysisComponent:
    """Component for displaying financial analysis results."""

    @staticmethod
    def display_analysis_result(result: AnalysisResult) -> None:
        """
        Display comprehensive analysis result.

        Args:
            result (AnalysisResult): Analysis result to display
        """
        # Main summary
        st.markdown("### 📊 Analysis Summary")
        st.markdown(result.summary)

        # Confidence and sentiment
        col1, col2 = st.columns(2)
        with col1:
            AnalysisComponent._display_confidence_meter(result.confidence_score)
        with col2:
            AnalysisComponent._display_sentiment_indicator(result.sentiment)

        # Key insights
        if result.key_insights:
            st.markdown("### 💡 Key Insights")
            for i, insight in enumerate(result.key_insights, 1):
                st.markdown(f"**{i}.** {insight}")

        # Mentioned tickers
        if result.mentioned_tickers:
            st.markdown("### 📈 Mentioned Stocks")
            AnalysisComponent._display_ticker_chips(result.mentioned_tickers)

        # Related news
        if result.top_news:
            st.markdown("### 📰 Related News")
            AnalysisComponent._display_news_items(result.top_news)

        # Remove sources section (not present in AnalysisResult)

    @staticmethod
    def _display_confidence_meter(confidence: float) -> None:
        """Display confidence score as a meter."""
        st.metric(
            label="Confidence Score",
            value=f"{confidence:.1%}",
            help="How confident the AI is in this analysis",
        )

        # Color-coded progress bar
        color = (
            UIConfig.SUCCESS_COLOR
            if confidence > 0.8
            else UIConfig.WARNING_COLOR if confidence > 0.5 else UIConfig.ERROR_COLOR
        )
        st.markdown(
            f"""
            <div style="background-color: #f0f0f0; border-radius: 10px; padding: 2px;">
                <div style="background-color: {color}; width: {confidence*100}%;
                           height: 20px; border-radius: 8px;"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def _display_sentiment_indicator(sentiment: str) -> None:
        """Display sentiment with appropriate emoji and color."""
        sentiment_config = {
            "positive": {
                "emoji": "📈",
                "color": UIConfig.SUCCESS_COLOR,
                "label": "Positive",
            },
            "negative": {
                "emoji": "📉",
                "color": UIConfig.ERROR_COLOR,
                "label": "Negative",
            },
            "neutral": {
                "emoji": "➡️",
                "color": UIConfig.WARNING_COLOR,
                "label": "Neutral",
            },
        }

        config = sentiment_config.get(sentiment.lower(), sentiment_config["neutral"])

        st.markdown(
            f"""
            <div style="text-align: center; padding: 10px; border-radius: 10px;
                       background-color: {config['color']}20; border: 2px solid {config['color']};">
                <h3 style="margin: 0; color: {config['color']};">
                    {config['emoji']} {config['label']}
                </h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def _display_ticker_chips(tickers: List[str]) -> None:
        """Display ticker symbols as clickable chips."""
        cols = st.columns(min(len(tickers), 5))
        for i, ticker in enumerate(tickers):
            with cols[i % 5]:
                if st.button(f"📊 {ticker}", key=f"ticker_{ticker}_{i}"):
                    st.session_state.selected_ticker = ticker
                    st.rerun()

    @staticmethod
    def _display_news_items(news_items: List[Dict[str, Any]]) -> None:
        """Display news items in expandable format."""
        for i, news in enumerate(news_items):
            with st.expander(f"📰 {news.get('title', 'News Item')}"):
                if "summary" in news:
                    st.markdown(news["summary"])
                if "url" in news:
                    st.markdown(f"[Read Full Article]({news['url']})")
                if "published_at" in news:
                    st.caption(f"Published: {news['published_at']}")


class InputComponent:
    """Component for handling user inputs."""

    @staticmethod
    def chat_input(
        placeholder: str = "Ask about financial markets, stocks, or economic trends...",
        key: str = "chat_input",
        on_submit: Optional[Callable[[str], None]] = None,
        value: Optional[str] = None,
    ) -> Optional[str]:
        """
        Create chat input field with validation.

        Args:
            placeholder (str): Input placeholder text
            key (str): Unique key for the input
            on_submit (Optional[Callable]): Callback function for submission

        Returns:
            Optional[str]: User input if submitted, None otherwise
        """
        user_input = st.chat_input(placeholder, key=key)

        if user_input and user_input.strip():
            if on_submit:
                on_submit(user_input.strip())
            return user_input.strip()

        return None

    @staticmethod
    def ticker_input(
        label: str = "Enter stock tickers (comma-separated)", key: str = "ticker_input"
    ) -> List[str]:
        """
        Create ticker input field with validation.

        Args:
            label (str): Input label
            key (str): Unique key for the input

        Returns:
            List[str]: List of validated ticker symbols
        """
        ticker_input = st.text_input(
            label,
            placeholder="e.g., AAPL, GOOGL, MSFT",
            key=key,
            help="Enter one or more stock ticker symbols separated by commas",
        )

        if ticker_input:
            # Parse and validate tickers
            tickers = [ticker.strip().upper() for ticker in ticker_input.split(",")]
            return [ticker for ticker in tickers if ticker and ticker.isalpha()]

        return []

    @staticmethod
    def file_uploader(
        label: str = "Upload financial document",
        accepted_types: List[str] = ["txt", "csv", "pdf"],
        key: str = "file_upload",
    ) -> Optional[str]:
        """
        Create file uploader with validation.

        Args:
            label (str): Uploader label
            accepted_types (List[str]): Accepted file types
            key (str): Unique key for the uploader

        Returns:
            Optional[str]: File content if uploaded, None otherwise
        """
        uploaded_file = st.file_uploader(
            label,
            type=accepted_types,
            key=key,
            help=f"Supported formats: {', '.join(accepted_types)}",
        )

        if uploaded_file is not None:
            try:
                # Read file content based on type
                if uploaded_file.type == "text/plain":
                    content = str(uploaded_file.read(), "utf-8")
                elif uploaded_file.type == "text/csv":
                    content = str(uploaded_file.read(), "utf-8")
                else:
                    content = str(uploaded_file.read(), "utf-8")

                return content
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                return None

        return None


class SidebarComponent:
    """Component for sidebar functionality."""

    @staticmethod
    def create_sidebar() -> Dict[str, Any]:
        """
        Create sidebar with configuration options.

        Returns:
            Dict[str, Any]: Sidebar configuration values
        """
        with st.sidebar:
            st.title("🏦 Finance GPT")
            st.markdown("---")

            # Configuration section
            st.subheader("⚙️ Configuration")

            config = {}

            # Model selection
            config["model"] = st.selectbox(
                "AI Model",
                [
                    "gemini-1.5-pro",
                    "gemini-1.5-flash",
                    "gemini-2.5-flash",
                    "gemini-2.5-pro",
                ],
                index=0,
                help="Choose the AI model for analysis",
            )

            # Analysis depth
            config["analysis_depth"] = st.select_slider(
                "Analysis Depth",
                options=["Quick", "Standard", "Detailed"],
                value="Standard",
                help="Choose the depth of financial analysis",
            )

            # Include news
            config["include_news"] = st.checkbox(
                "Include Recent News",
                value=True,
                help="Include recent financial news in analysis",
            )

            # Max results
            config["max_results"] = st.slider(
                "Max News Articles",
                min_value=1,
                max_value=20,
                value=5,
                help="Maximum number of news articles to include",
            )

            st.markdown("---")

            # Session management
            st.subheader("💾 Session")

            if st.button("🗑️ Clear Chat History", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

            if st.button("📥 Export Chat", use_container_width=True):
                SidebarComponent._export_chat_history()

            # Statistics
            st.markdown("---")
            st.subheader("📊 Statistics")

            if hasattr(st.session_state, "chat_history"):
                total_messages = len(st.session_state.chat_history)
                user_messages = len(
                    [m for m in st.session_state.chat_history if m.role == "user"]
                )
                st.metric("Total Messages", total_messages)
                st.metric("Your Questions", user_messages)

            return config

    @staticmethod
    def _export_chat_history() -> None:
        """Export chat history as downloadable file."""
        if (
            not hasattr(st.session_state, "chat_history")
            or not st.session_state.chat_history
        ):
            st.warning("No chat history to export")
            return

        # Format chat history for export
        export_data = []
        for message in st.session_state.chat_history:
            export_data.append(
                {
                    "timestamp": message.timestamp.isoformat(),
                    "role": message.role,
                    "content": message.content,
                }
            )

        import json

        export_json = json.dumps(export_data, indent=2)

        st.download_button(
            label="📄 Download JSON",
            data=export_json,
            file_name=f"finance_gpt_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )


class MetricsComponent:
    """Component for displaying metrics and KPIs."""

    @staticmethod
    def display_metrics_grid(metrics: Dict[str, Any]) -> None:
        """
        Display metrics in a grid layout.

        Args:
            metrics (Dict[str, Any]): Dictionary of metrics to display
        """
        if not metrics:
            return

        # Create columns based on number of metrics
        num_metrics = len(metrics)
        cols = st.columns(min(num_metrics, 4))

        for i, (key, value) in enumerate(metrics.items()):
            with cols[i % 4]:
                if isinstance(value, dict):
                    st.metric(
                        label=value.get("label", key),
                        value=value.get("value", "N/A"),
                        delta=value.get("delta"),
                        help=value.get("help"),
                    )
                else:
                    st.metric(label=key, value=value)

    @staticmethod
    def display_performance_metrics() -> None:
        """Display system performance metrics."""
        if hasattr(st.session_state, "performance_metrics"):
            metrics = st.session_state.performance_metrics

            st.subheader("⚡ Performance Metrics")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Response Time",
                    f"{metrics.get('response_time', 0):.2f}s",
                    help="Average response time for queries",
                )

            with col2:
                st.metric(
                    "Success Rate",
                    f"{metrics.get('success_rate', 0):.1%}",
                    help="Percentage of successful queries",
                )

            with col3:
                st.metric(
                    "Cache Hit Rate",
                    f"{metrics.get('cache_hit_rate', 0):.1%}",
                    help="Percentage of queries served from cache",
                )
