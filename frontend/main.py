"""
Main entry point for Finance GPT Streamlit application.

This module serves as the primary entry point for the Streamlit app,
initializing all components and orchestrating the application flow.
"""

import streamlit as st
import sys
from pathlib import Path
from decouple import config as env_config

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Also add the frontend directory to path
frontend_dir = Path(__file__).parent
sys.path.insert(0, str(frontend_dir))

try:
    from frontend.components.chat_interface import ChatInterface
    from frontend.core.config import AppConfig, UIConfig
    from frontend.core.state_manager import StateManager
    from frontend.utils.ui_helpers import UIHelpers
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.error("Please ensure all required modules are installed and accessible.")
    st.stop()


def configure_page():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title=AppConfig.APP_NAME,
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded",
        
        menu_items={
            "Get Help": "https://github.com/hallelx2/finance-gpt",
            "Report a bug": "https://github.com/hallelx2/finance-gpt/issues",
            "About": f"""
            # {AppConfig.APP_NAME}

            **Version:** {AppConfig.APP_VERSION}

            An AI-powered financial market analysis assistant that provides
            real-time insights, market analysis, and investment guidance.

            **Features:**
            - Real-time market data analysis
            - AI-powered financial insights
            - Interactive chat interface
            - Comprehensive market research

            Built with Streamlit, LangChain, and Google Generative AI.
            """,
        },
    )


def check_environment():
    """Check if the environment is properly configured using python-decouple."""
    missing_vars = []

    # Check for required environment variables
    required_env_vars = [
        "GOOGLE_API_KEY",
        "FINNHUB_API_KEY",
        "MONGODB_CONNECTION_STRING",
    ]

    for var in required_env_vars:
        if env_config(var, default=None) is None:
            missing_vars.append(var)

    if missing_vars:
        st.error("⚠️ Missing Environment Variables")
        st.markdown(
            """
        The following environment variables are required but not set:
        """
        )
        for var in missing_vars:
            st.code(f"{var}")

        st.markdown(
            """
        **To fix this:**
        1. Create a `.env` file in your project root
        2. Add the required variables:
        ```
        GOOGLE_API_KEY=your_google_api_key_here
        FINNHUB_API_KEY=your_finnhub_api_key_here
        MONGODB_CONNECTION_STRING=your_mongodb_connection_string_here
        ```
        3. Restart the application

        **Getting API Keys:**
        - **Google API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
        - **FinnHub API Key**: Get from [FinnHub](https://finnhub.io/register)
        - **MongoDB**: Create cluster at [MongoDB Atlas](https://cloud.mongodb.com/)
        """
        )

        return False

    return True


def initialize_application():
    """Initialize the application with necessary setup."""
    try:
        # Check environment configuration
        if not check_environment():
            st.stop()

        # Initialize state manager (session is initialized in __init__)
        state_manager = StateManager()

        return True

    except Exception as e:
        st.error(f"Initialization Error: {str(e)}")
        st.error("Please check your configuration and try again.")
        return False


def display_header():
    """Display the application header."""
    st.markdown(
        f"""
        <div style="text-align: center; padding: 1rem 0; margin-bottom: 2rem;
                   background: linear-gradient(90deg, #1f4e79 0%, #2e86ab 100%);
                   border-radius: 10px; color: white;">
            <h1 style="margin: 0; font-size: 2.5rem;">🏦 {AppConfig.APP_NAME}</h1>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
                Your AI-Powered Financial Market Analysis Assistant
            </p>
            <p style="margin: 0.2rem 0 0 0; font-size: 0.9rem; opacity: 0.7;">
                Version {AppConfig.APP_VERSION} | Real-time Market Insights
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_footer():
    """Display the application footer."""
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; padding: 1rem; color: #666; font-size: 0.8rem;">
            <p>
                {AppConfig.APP_NAME} v{AppConfig.APP_VERSION} |
                Built with ❤️ using Streamlit, LangChain & Google AI |
                <a href="https://github.com/hallelx2/finance-gpt" target="_blank">GitHub</a>
            </p>
            <p style="margin-top: 0.5rem; font-size: 0.7rem;">
                ⚠️ <strong>Disclaimer:</strong> This application provides AI-generated financial analysis
                for informational purposes only. Not financial advice. Always consult with qualified
                financial professionals before making investment decisions.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def handle_errors():
    """Global error handler for the application."""
    if hasattr(st.session_state, "error_occurred") and st.session_state.error_occurred:
        st.error(
            "An error occurred. Please refresh the page or contact support if the issue persists."
        )

        # Clear error state
        st.session_state.error_occurred = False


def main():
    """Main application function."""
    try:
        # Configure page
        configure_page()

        # Initialize application
        if not initialize_application():
            return

        # Handle any global errors
        handle_errors()

        # Display header
        display_header()

        # Create and run chat interface
        chat_interface = ChatInterface()
        chat_interface.render()

        # Display footer
        display_footer()

    except KeyboardInterrupt:
        st.info("Application interrupted by user.")

    except Exception as e:
        st.error("🚨 Critical Application Error")
        st.error(f"Error: {str(e)}")

        # Show error details in expander
        with st.expander("🔍 Error Details (for debugging)"):
            import traceback

            st.code(traceback.format_exc())

        st.markdown(
            """
        **Troubleshooting Steps:**
        1. Refresh the page (F5)
        2. Check your internet connection
        3. Verify environment variables are set correctly
        4. Restart the application
        5. If the issue persists, please report it on GitHub
        """
        )

        # Set error state
        st.session_state.error_occurred = True


def run_dev_server():
    """Run the development server with additional debugging."""
    import logging

    # Configure logging for development
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting Finance GPT Streamlit application...")

    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    # Check if running in development mode
    if env_config("STREAMLIT_ENV", default="production") == "development":
        run_dev_server()
    else:
        main()
