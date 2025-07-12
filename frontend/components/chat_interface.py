"""
Main chat interface component for Finance GPT Streamlit application.

Orchestrates the chat experience, integrating all components and handling user interactions.
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import traceback

from frontend.core.state_manager import StateManager, ChatMessage, AnalysisResult
from frontend.components.ui_components import (
    MessageComponent,
    StatusComponent,
    AnalysisComponent,
    InputComponent,
    SidebarComponent,
    MetricsComponent,
)
from frontend.utils.validators import InputValidator
from frontend.utils.formatters import MessageFormatter
from frontend.core.config import AppConfig, UIConfig

# Try to import RAG pipeline with fallback
try:
    from frontend.rag.rag_pipeline import RAGPipeline
except ImportError as e:
    st.error(f"RAGPipeline import failed: {e}")
    st.code(traceback.format_exc())
    raise


class ChatInterface:
    """Main chat interface orchestrating the Finance GPT conversation flow."""

    def __init__(self):
        """Initialize the chat interface."""
        self.state_manager = StateManager()
        self.rag_pipeline = None
        self._initialize_rag_pipeline()

    def _initialize_rag_pipeline(self) -> None:
        """Initialize the RAG pipeline with error handling."""
        try:
            if RAGPipeline is not None:
                self.rag_pipeline = RAGPipeline()
            else:
                self.rag_pipeline = None
        except Exception as e:
            st.warning(f"RAG pipeline not available: {str(e)}")
            self.rag_pipeline = None

    def render(self) -> None:
        """Render the complete chat interface."""
        # Configure page
        st.set_page_config(
            page_title="Finance GPT",
            page_icon="🏦",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        # Custom CSS
        self._inject_custom_css()

        # Initialize session state
        self.state_manager

        # Render sidebar
        sidebar_config = SidebarComponent.create_sidebar()

        # Main content area
        self._render_main_content(sidebar_config)

    def _inject_custom_css(self) -> None:
        """Inject custom CSS for styling."""
        st.markdown(
            f"""
            <style>
            .main {{
                padding-top: 1rem;
            }}

            .chat-container {{
                max-height: 600px;
                overflow-y: auto;
                padding: 1rem;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                background-color: #fafafa;
            }}

            .user-message {{
                background-color: {UIConfig.USER_MESSAGE_COLOR};
                padding: 10px;
                border-radius: 10px;
                margin: 5px 0;
                margin-left: 20%;
            }}

            .assistant-message {{
                background-color: {UIConfig.ASSISTANT_MESSAGE_COLOR};
                padding: 10px;
                border-radius: 10px;
                margin: 5px 0;
                margin-right: 20%;
            }}

            .metric-card {{
                background-color: white;
                padding: 1rem;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin: 0.5rem 0;
            }}

            .status-indicator {{
                position: fixed;
                top: 10px;
                right: 10px;
                z-index: 1000;
            }}

            .ticker-chip {{
                display: inline-block;
                background-color: {UIConfig.ACCENT_COLOR};
                color: white;
                padding: 5px 10px;
                border-radius: 15px;
                margin: 2px;
                font-size: 0.8rem;
            }}

            .confidence-meter {{
                background: linear-gradient(90deg, #ff4444 0%, #ffaa00 50%, #00aa00 100%);
                height: 20px;
                border-radius: 10px;
                position: relative;
            }}

            .error-container {{
                background-color: #ffe6e6;
                border: 1px solid #ff9999;
                border-radius: 5px;
                padding: 10px;
                margin: 10px 0;
            }}

            .success-container {{
                background-color: #e6ffe6;
                border: 1px solid #99ff99;
                border-radius: 5px;
                padding: 10px;
                margin: 10px 0;
            }}

            .loading-spinner {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100px;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

    def _render_main_content(self, sidebar_config: Dict[str, Any]) -> None:
        """
        Render the main content area.

        Args:
            sidebar_config (Dict[str, Any]): Configuration from sidebar
        """
        # Header
        st.title("🏦 Finance GPT")
        st.markdown("*Your AI-powered financial market analysis assistant*")

        # Check RAG pipeline status
        if not self.rag_pipeline:
            StatusComponent.show_error(
                "RAG Pipeline Not Available",
                "The financial analysis system is currently unavailable. Please check your configuration.",
            )
            return

        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Analytics", "⚙️ Settings"])

        with tab1:
            self._render_chat_tab(sidebar_config)

        with tab2:
            self._render_analytics_tab()

        with tab3:
            self._render_settings_tab()

    def _render_chat_tab(self, config: Dict[str, Any]) -> None:
        """
        Render the main chat interface.

        Args:
            config (Dict[str, Any]): Configuration settings
        """
        # Chat history container
        chat_container = st.container()

        with chat_container:
            st.subheader("💬 Conversation")

            # Display chat history
            if (
                hasattr(st.session_state, "chat_history")
                and st.session_state.chat_history
            ):
                with st.container():
                    MessageComponent.display_message_list(st.session_state.chat_history)
            else:
                st.info(
                    "👋 Welcome! Ask me anything about financial markets, stocks, or economic trends."
                )
                self._show_sample_questions()

        # Chat input
        st.markdown("---")
        chat_input_value = (
            st.session_state.pop("pending_chat_input", None)
            if "pending_chat_input" in st.session_state
            else None
        )
        user_input = InputComponent.chat_input(
            placeholder="Ask about financial markets, stocks, or economic trends...",
            key="main_chat_input",
            value=chat_input_value,
        )

        # Process user input
        if user_input:
            self._process_user_input(user_input, config)

    def _show_sample_questions(self) -> None:
        """Display sample questions to help users get started."""
        st.markdown("### 💡 Sample Questions")

        sample_questions = [
            "What's the current market outlook for tech stocks?",
            "How is Apple (AAPL) performing this quarter?",
            "What are the latest trends in cryptocurrency markets?",
            "Analyze the impact of recent Fed decisions on the market",
            "What should I know about ESG investing trends?",
        ]

        def set_sample_question(q):
            st.session_state["pending_chat_input"] = q

        cols = st.columns(2)
        for i, question in enumerate(sample_questions):
            with cols[i % 2]:
                st.button(
                    f"💭 {question}",
                    key=f"sample_q_{i}",
                    use_container_width=True,
                    on_click=set_sample_question,
                    args=(question,),
                )

    def _process_user_input(self, user_input: str, config: Dict[str, Any]) -> None:
        """
        Process user input and generate response.

        Args:
            user_input (str): User's question/input
            config (Dict[str, Any]): Configuration settings
        """
        # Validate input
        is_valid, error_message = InputValidator.validate_query(user_input)
        if not is_valid:
            StatusComponent.show_error("Invalid Input", error_message)
            return

        # Add user message to chat history
        self.state_manager.add_message(
            role="user",
            content=user_input
        )

        # Show processing status
        with st.spinner("🤔 Analyzing your question..."):
            try:
                # Process with RAG pipeline
                response = self._get_rag_response(user_input, config)

                if response:
                    # Add assistant response to chat history
                    self.state_manager.add_message(
                        role="assistant",
                        content=response.get("summary", "Analysis completed."),
                        metadata=response
                    )

                    # Display structured response
                    self._display_structured_response(response)

                    StatusComponent.show_success("Analysis completed successfully!")
                else:
                    StatusComponent.show_error(
                        "Failed to generate response", "Please try again."
                    )

            except Exception as e:
                error_message = f"Error processing your request: {str(e)}"
                StatusComponent.show_error("Processing Error", error_message)

                # Add error message to chat history
                self.state_manager.add_message(
                    role="system",
                    content=f"Error: {error_message}"
                )

        # Rerun to update chat display
        st.rerun()

    def _get_rag_response(
        self, query: str, config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get response from RAG pipeline.

        Args:
            query (str): User query
            config (Dict[str, Any]): Configuration settings

        Returns:
            Optional[Dict[str, Any]]: RAG response or None if failed
        """
        try:
            # Configure RAG pipeline based on sidebar settings
            rag_config = {
                "model": config.get("model", "gemini-1.5-pro"),
                "include_news": config.get("include_news", True),
                "max_results": config.get("max_results", 5),
                "analysis_depth": config.get("analysis_depth", "Standard"),
            }

            # Process query through RAG pipeline
            if self.rag_pipeline is not None and hasattr(self.rag_pipeline, "process_query"):
                return self.rag_pipeline.process_query(query, **rag_config)
            else:
                # Fallback to basic processing
                return self._fallback_response(query)

        except Exception as e:
            st.error(f"RAG Pipeline Error: {str(e)}")
            return None

    def _fallback_response(self, query: str) -> Dict[str, Any]:
        """
        Generate fallback response when RAG pipeline is unavailable.

        Args:
            query (str): User query

        Returns:
            Dict[str, Any]: Fallback response
        """
        return {
            "summary": f"I received your question about: '{query}'. However, the full analysis system is currently unavailable. Please check the system configuration and try again.",
            "key_insights": [
                "System is in fallback mode",
                "Full financial analysis unavailable",
                "Please check configuration",
            ],
            "mentioned_tickers": [],
            "sentiment": "neutral",
            "confidence_score": 0.1,
            "related_news": [],
            "sources": [],
        }

    def _display_structured_response(self, response: Dict[str, Any]) -> None:
        """
        Display structured response from RAG pipeline.

        Args:
            response (Dict[str, Any]): Response data to display
        """
        # Create AnalysisResult object
        analysis_result = AnalysisResult(
            summary=response.get("summary", ""),
            key_insights=response.get("key_insights", []),
            mentioned_tickers=response.get("mentioned_tickers", []),
            sentiment=response.get("sentiment", "neutral"),
            confidence_score=response.get("confidence_score", 0.5),
            top_news=response.get("related_news", []),
        )

        # Display using AnalysisComponent
        AnalysisComponent.display_analysis_result(analysis_result)

    def _render_analytics_tab(self) -> None:
        """Render the analytics/metrics tab."""
        st.subheader("📊 Analytics Dashboard")

        # Performance metrics
        if hasattr(st.session_state, "performance_metrics"):
            MetricsComponent.display_performance_metrics()
        else:
            st.info(
                "No performance metrics available yet. Start a conversation to see analytics."
            )

        # Chat statistics
        if hasattr(st.session_state, "chat_history") and st.session_state.chat_history:
            self._display_chat_analytics()
        else:
            st.info("No chat data available for analytics.")

    def _display_chat_analytics(self) -> None:
        """Display analytics about chat history."""
        chat_history = st.session_state.chat_history

        # Basic statistics
        total_messages = len(chat_history)
        user_messages = [msg for msg in chat_history if msg.role == "user"]
        assistant_messages = [msg for msg in chat_history if msg.role == "assistant"]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Messages", total_messages)
        with col2:
            st.metric("Your Questions", len(user_messages))
        with col3:
            st.metric("AI Responses", len(assistant_messages))

        # Message timeline
        st.markdown("### 📈 Message Timeline")
        if chat_history:
            timestamps = [msg.timestamp for msg in chat_history]
            roles = [msg.role for msg in chat_history]

            # Create simple timeline visualization
            timeline_data = []
            for timestamp, role in zip(timestamps, roles):
                timeline_data.append(
                    {
                        "Time": timestamp.strftime("%H:%M:%S"),
                        "Role": role.title(),
                        "Count": 1,
                    }
                )

            if timeline_data:
                st.bar_chart(timeline_data)

    def _render_settings_tab(self) -> None:
        """Render the settings/configuration tab."""
        st.subheader("⚙️ Configuration Settings")

        # API Configuration
        with st.expander("🔑 API Configuration"):
            st.text_input(
                "Google API Key",
                type="password",
                help="Enter your Google Generative AI API key",
                key="google_api_key",
            )
            st.text_input(
                "FinnHub API Key",
                type="password",
                help="Enter your FinnHub API key for financial data",
                key="finnhub_api_key",
            )
            st.text_input(
                "MongoDB Connection String",
                type="password",
                help="Enter your MongoDB Atlas connection string",
                key="mongodb_connection",
            )

        # System Configuration
        with st.expander("🛠️ System Settings"):
            st.number_input(
                "Request Timeout (seconds)",
                min_value=5,
                max_value=300,
                value=30,
                help="Timeout for API requests",
            )
            st.number_input(
                "Max Retries",
                min_value=1,
                max_value=10,
                value=3,
                help="Maximum number of retries for failed requests",
            )
            st.selectbox(
                "Log Level",
                ["DEBUG", "INFO", "WARNING", "ERROR"],
                index=1,
                help="System logging level",
            )

        # Data Management
        with st.expander("💾 Data Management"):
            if st.button("🗑️ Clear All Data", type="primary"):
                if st.checkbox("I understand this will delete all chat history"):
                    self.state_manager.clear_all_data()
                    st.success("All data cleared successfully!")
                    st.rerun()

            if st.button("📤 Export Data"):
                self._export_all_data()

            uploaded_file = st.file_uploader(
                "📥 Import Chat History",
                type=["json"],
                help="Upload a previously exported chat history file",
            )

            if uploaded_file:
                self._import_chat_history(uploaded_file)

    def _export_all_data(self) -> None:
        """Export all application data."""
        try:
            export_data = self.state_manager.export_session_data()

            import json

            export_json = json.dumps(export_data, indent=2, default=str)

            st.download_button(
                label="📄 Download Complete Data Export",
                data=export_json,
                file_name=f"finance_gpt_complete_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
            )

            StatusComponent.show_success("Data export ready for download!")

        except Exception as e:
            StatusComponent.show_error("Export Failed", str(e))

    def _import_chat_history(self, uploaded_file) -> None:
        """
        Import chat history from uploaded file.

        Args:
            uploaded_file: Streamlit uploaded file object
        """
        try:
            import json

            # Read and parse JSON
            content = json.loads(uploaded_file.read())

            # Validate and import
            if self.state_manager.import_session_data(content):
                StatusComponent.show_success("Chat history imported successfully!")
                st.rerun()
            else:
                StatusComponent.show_error(
                    "Import Failed", "Invalid file format or data structure."
                )

        except Exception as e:
            StatusComponent.show_error("Import Error", str(e))

    def run(self) -> None:
        """Run the chat interface application."""
        try:
            self.render()
        except Exception as e:
            st.error(f"Application Error: {str(e)}")
            st.code(traceback.format_exc())


# Main entry point for the chat interface
def main():
    """Main function to run the Finance GPT chat interface."""
    chat_interface = ChatInterface()
    chat_interface.run()


if __name__ == "__main__":
    main()
