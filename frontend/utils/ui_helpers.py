"""
UI helper utilities for Finance GPT Streamlit application.

Contains common UI operations, styling helpers, and interface enhancements.
"""

import streamlit as st
from typing import Optional
import time
from datetime import datetime

from frontend.core.config import config, UIConstants, SampleData


class UIHelpers:
    """Collection of UI helper methods for Streamlit interface."""

    @staticmethod
    def setup_page_config():
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title=config.PAGE_TITLE,
            page_icon=config.PAGE_ICON,
            layout=config.LAYOUT,
            initial_sidebar_state=config.INITIAL_SIDEBAR_STATE,
            menu_items={
                "Get Help": "https://github.com/hallelx2/finance-gpt",
                "Report a bug": "https://github.com/hallelx2/finance-gpt/issues",
                "About": f"# {config.APP_NAME}\n{config.APP_DESCRIPTION}\n\nVersion: {config.APP_VERSION}",
            },
        )

    @staticmethod
    def apply_custom_css():
        """Apply custom CSS styling to the Streamlit app."""
        st.markdown(
            """
        <style>
            /* Main container styling */
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }

            /* Hide Streamlit menu and footer */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}

            /* Custom chat container */
            .chat-container {
                height: 500px;
                overflow-y: auto;
                padding: 1rem;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                background: #fafafa;
            }

            /* Input styling */
            .stTextInput > div > div > input {
                border-radius: 20px;
                border: 2px solid #e0e0e0;
                padding: 10px 15px;
                font-size: 16px;
            }

            .stTextInput > div > div > input:focus {
                border-color: #1976d2;
                box-shadow: 0 0 0 0.2rem rgba(25, 118, 210, 0.25);
            }

            /* Button styling */
            .stButton > button {
                border-radius: 20px;
                border: none;
                padding: 10px 20px;
                font-weight: bold;
                transition: all 0.3s ease;
            }

            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }

            /* Sidebar styling */
            .sidebar .sidebar-content {
                padding-top: 1rem;
            }

            /* Metric cards */
            .metric-card {
                background: white;
                padding: 1rem;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin: 0.5rem 0;
            }

            /* Status indicators */
            .status-indicator {
                display: inline-flex;
                align-items: center;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
                margin: 2px;
            }

            .status-processing {
                background: #fff3e0;
                color: #e65100;
                border: 1px solid #ffcc02;
            }

            .status-success {
                background: #e8f5e8;
                color: #2e7d32;
                border: 1px solid #4caf50;
            }

            .status-error {
                background: #ffebee;
                color: #c62828;
                border: 1px solid #f44336;
            }

            /* Animation classes */
            .fade-in {
                animation: fadeIn 0.5s ease-in;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .pulse {
                animation: pulse 2s infinite;
            }

            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.7; }
                100% { opacity: 1; }
            }

            /* Responsive design */
            @media (max-width: 768px) {
                .main .block-container {
                    padding-left: 1rem;
                    padding-right: 1rem;
                }

                .chat-container {
                    height: 400px;
                }
            }
        </style>
        """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def create_header():
        """Create the application header."""
        st.markdown(
            f"""
        <div style="
            background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
            padding: 2rem 1rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        ">
            <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">
                {config.PAGE_ICON} {config.APP_NAME}
            </h1>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">
                {config.APP_DESCRIPTION}
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def create_quick_actions():
        """Create quick action buttons for common queries."""
        st.markdown("### 💡 Quick Actions")

        cols = st.columns(2)

        with cols[0]:
            if st.button("📊 Market Overview", key="market_overview"):
                return "What's the current market overview and sentiment?"

        with cols[1]:
            if st.button("🔥 Trending Stocks", key="trending_stocks"):
                return "What are the trending stocks today?"

        # Sample questions in expander
        with st.expander("📝 Sample Questions"):
            for i, question in enumerate(SampleData.SAMPLE_QUESTIONS[:4]):
                if st.button(f"💬 {question}", key=f"sample_{i}"):
                    return question

        return None

    @staticmethod
    def create_status_indicator(status: str, message: str) -> str:
        """Create a status indicator with message."""
        status_configs = {
            "processing": {
                "class": "status-processing",
                "icon": UIConstants.ICONS["loading"],
                "color": "#e65100",
            },
            "success": {
                "class": "status-success",
                "icon": UIConstants.ICONS["success"],
                "color": "#2e7d32",
            },
            "error": {
                "class": "status-error",
                "icon": UIConstants.ICONS["error"],
                "color": "#c62828",
            },
            "info": {
                "class": "status-info",
                "icon": UIConstants.ICONS["info"],
                "color": "#1976d2",
            },
        }

        config_item = status_configs.get(status, status_configs["info"])

        return f"""
        <div class="status-indicator {config_item['class']}">
            <span style="margin-right: 6px;">{config_item['icon']}</span>
            {message}
        </div>
        """

    @staticmethod
    def create_metric_card(
        title: str, value: str, delta: Optional[str] = None, icon: Optional[str] = None
    ) -> str:
        """Create a metric display card."""
        icon_html = (
            f'<span style="font-size: 1.5rem; margin-right: 10px;">{icon}</span>'
            if icon
            else ""
        )
        delta_html = (
            f'<div style="font-size: 0.9rem; color: #666; margin-top: 4px;">{delta}</div>'
            if delta
            else ""
        )

        return f"""
        <div class="metric-card">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                {icon_html}
                <div style="font-size: 0.9rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px;">
                    {title}
                </div>
            </div>
            <div style="font-size: 2rem; font-weight: bold; color: #333;">
                {value}
            </div>
            {delta_html}
        </div>
        """

    @staticmethod
    def create_loading_spinner(message: str = "Processing...") -> None:
        """Create a loading spinner with message."""
        st.markdown(
            f"""
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            background: #f8f9fa;
            border-radius: 10px;
            margin: 1rem 0;
        ">
            <div style="
                width: 40px;
                height: 40px;
                border: 4px solid #e3f2fd;
                border-top: 4px solid #1976d2;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-right: 15px;
            "></div>
            <span style="font-size: 1.1rem; color: #1976d2; font-weight: 500;">
                {message}
            </span>
        </div>

        <style>
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
        """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def create_progress_bar(progress: float, message: str = "") -> None:
        """Create a custom progress bar."""
        percentage = int(progress * 100)

        st.markdown(
            f"""
        <div style="margin: 1rem 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="font-size: 0.9rem; color: #666;">{message}</span>
                <span style="font-size: 0.9rem; font-weight: bold; color: #1976d2;">{percentage}%</span>
            </div>
            <div style="
                background: #e0e0e0;
                height: 8px;
                border-radius: 4px;
                overflow: hidden;
            ">
                <div style="
                    background: linear-gradient(90deg, #1976d2 0%, #42a5f5 100%);
                    height: 100%;
                    width: {percentage}%;
                    transition: width 0.3s ease;
                    border-radius: 4px;
                "></div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    @staticmethod
    def show_toast(message: str, toast_type: str = "info", duration: int = 3):
        """Show a toast notification."""
        toast_configs = {
            "success": {"color": "#4caf50", "icon": UIConstants.ICONS["success"]},
            "error": {"color": "#f44336", "icon": UIConstants.ICONS["error"]},
            "warning": {"color": "#ff9800", "icon": UIConstants.ICONS["warning"]},
            "info": {"color": "#2196f3", "icon": UIConstants.ICONS["info"]},
        }

        config_item = toast_configs.get(toast_type, toast_configs["info"])

        toast_placeholder = st.empty()
        toast_placeholder.markdown(
            f"""
        <div style="
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            color: {config_item['color']};
            padding: 12px 16px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border-left: 4px solid {config_item['color']};
            z-index: 1000;
            animation: slideIn 0.3s ease;
        ">
            <div style="display: flex; align-items: center;">
                <span style="margin-right: 8px;">{config_item['icon']}</span>
                <span>{message}</span>
            </div>
        </div>

        <style>
            @keyframes slideIn {{
                from {{ transform: translateX(100%); opacity: 0; }}
                to {{ transform: translateX(0); opacity: 1; }}
            }}
        </style>
        """,
            unsafe_allow_html=True,
        )

        # Auto-hide after duration
        time.sleep(duration)
        toast_placeholder.empty()

    @staticmethod
    def create_collapsible_section(
        title: str, content: str, expanded: bool = False
    ) -> None:
        """Create a collapsible section."""
        with st.expander(title, expanded=expanded):
            st.markdown(content, unsafe_allow_html=True)

    @staticmethod
    def format_timestamp(timestamp: datetime) -> str:
        """Format timestamp for display."""
        now = datetime.now()
        diff = now - timestamp

        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"

    @staticmethod
    def create_copy_button(text: str, button_text: str = "Copy") -> bool:
        """Create a copy-to-clipboard button."""
        if st.button(f"📋 {button_text}"):
            st.write(f"```\n{text}\n```")
            st.success("Text ready to copy!")
            return True
        return False

    @staticmethod
    def safe_markdown(content: str, **kwargs) -> None:
        """Safely render markdown content."""
        try:
            st.markdown(content, **kwargs)
        except Exception as e:
            st.error(f"Error rendering content: {str(e)}")
            st.text(content)  # Fallback to plain text

    @staticmethod
    def create_download_button(
        data: str, filename: str, label: str = "Download"
    ) -> None:
        """Create a download button for data."""
        st.download_button(
            label=f"💾 {label}", data=data, file_name=filename, mime="text/plain"
        )
