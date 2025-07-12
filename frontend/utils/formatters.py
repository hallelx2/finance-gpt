"""
Formatter utilities for Finance GPT Streamlit application.

Contains formatting functions for messages, data display, and analysis results.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import re

from frontend.core.config import UIConstants
from frontend.core.state_manager import ChatMessage, AnalysisResult


class MessageFormatter:
    """Formats chat messages for display."""

    @staticmethod
    def format_user_message(message: ChatMessage) -> str:
        """Format user message for display."""
        timestamp = message.timestamp.strftime("%H:%M")
        return f"""
        <div style="
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            padding: 12px 16px;
            border-radius: 15px 15px 5px 15px;
            margin: 8px 0;
            border-left: 4px solid #1976d2;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-width: 80%;
            margin-left: auto;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <span style="font-size: 16px; margin-right: 8px;">{UIConstants.ICONS['user']}</span>
                <strong style="color: #1976d2;">You</strong>
                <span style="margin-left: auto; font-size: 12px; color: #666;">{timestamp}</span>
            </div>
            <div style="color: #333; line-height: 1.4;">
                {message.content}
            </div>
        </div>
        """

    @staticmethod
    def format_assistant_message(message: ChatMessage) -> str:
        """Format assistant message for display."""
        timestamp = message.timestamp.strftime("%H:%M")

        # Process markdown-like content
        content = MessageFormatter._process_markdown(message.content)

        return f"""
        <div style="
            background: linear-gradient(135deg, #f5f5f5 0%, #e8f5e8 100%);
            padding: 12px 16px;
            border-radius: 15px 15px 15px 5px;
            margin: 8px 0;
            border-left: 4px solid #4caf50;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-width: 85%;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <span style="font-size: 16px; margin-right: 8px;">{UIConstants.ICONS['assistant']}</span>
                <strong style="color: #4caf50;">Finance GPT</strong>
                <span style="margin-left: auto; font-size: 12px; color: #666;">{timestamp}</span>
            </div>
            <div style="color: #333; line-height: 1.5;">
                {content}
            </div>
        </div>
        """

    @staticmethod
    def format_error_message(message: str, timestamp: Optional[datetime] = None) -> str:
        """Format error message for display."""
        if timestamp is None:
            timestamp = datetime.now()

        time_str = timestamp.strftime("%H:%M")

        return f"""
        <div style="
            background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
            padding: 12px 16px;
            border-radius: 15px;
            margin: 8px 0;
            border-left: 4px solid #f44336;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <span style="font-size: 16px; margin-right: 8px;">{UIConstants.ICONS['error']}</span>
                <strong style="color: #f44336;">Error</strong>
                <span style="margin-left: auto; font-size: 12px; color: #666;">{time_str}</span>
            </div>
            <div style="color: #333; line-height: 1.4;">
                {message}
            </div>
        </div>
        """

    @staticmethod
    def _process_markdown(content: str) -> str:
        """Process basic markdown formatting."""
        # Headers
        content = re.sub(
            r"^## (.+)$",
            r'<h3 style="color: #1976d2; margin: 15px 0 10px 0; font-size: 18px;">\1</h3>',
            content,
            flags=re.MULTILINE,
        )
        content = re.sub(
            r"^### (.+)$",
            r'<h4 style="color: #1976d2; margin: 12px 0 8px 0; font-size: 16px;">\1</h4>',
            content,
            flags=re.MULTILINE,
        )

        # Bold text
        content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", content)

        # Bullet points
        content = re.sub(
            r"^• (.+)$",
            r'<li style="margin: 5px 0;">\1</li>',
            content,
            flags=re.MULTILINE,
        )

        # Wrap consecutive list items in ul tags
        content = re.sub(
            r"(<li.*?</li>\s*)+",
            r'<ul style="margin: 10px 0; padding-left: 20px;">\g<0></ul>',
            content,
        )

        # Line breaks
        content = content.replace("\n", "<br>")

        return content


class DataFormatter:
    """Formats data for display in the UI."""

    @staticmethod
    def format_analysis_summary(analysis: AnalysisResult) -> str:
        """Format analysis result as a summary card."""
        sentiment_color = {
            "positive": UIConstants.POSITIVE_COLOR,
            "negative": UIConstants.NEGATIVE_COLOR,
            "neutral": UIConstants.NEUTRAL_COLOR,
        }.get(analysis.sentiment, UIConstants.NEUTRAL_COLOR)

        sentiment_emoji = UIConstants.ICONS.get(
            f"sentiment_{analysis.sentiment}", UIConstants.ICONS["sentiment_neutral"]
        )

        tickers_display = (
            ", ".join(analysis.mentioned_tickers)
            if analysis.mentioned_tickers
            else "General Market"
        )
        confidence_percentage = int(analysis.confidence_score * 100)

        return f"""
        <div style="
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 16px;
            border-radius: 12px;
            margin: 10px 0;
            border: 1px solid #dee2e6;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h4 style="margin: 0; color: #495057; font-size: 16px;">
                    {UIConstants.ICONS['insights']} Analysis Summary
                </h4>
                <span style="font-size: 12px; color: #6c757d;">
                    {analysis.processing_time:.1f}s
                </span>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-bottom: 12px;">
                <div style="text-align: center;">
                    <div style="font-size: 14px; color: #6c757d; margin-bottom: 4px;">
                        {UIConstants.ICONS['stocks']} Stocks
                    </div>
                    <div style="font-weight: bold; color: #495057; font-size: 12px;">
                        {tickers_display}
                    </div>
                </div>

                <div style="text-align: center;">
                    <div style="font-size: 14px; color: #6c757d; margin-bottom: 4px;">
                        Sentiment
                    </div>
                    <div style="font-weight: bold; color: {sentiment_color};">
                        {sentiment_emoji} {analysis.sentiment.title()}
                    </div>
                </div>

                <div style="text-align: center;">
                    <div style="font-size: 14px; color: #6c757d; margin-bottom: 4px;">
                        {UIConstants.ICONS['confidence']} Confidence
                    </div>
                    <div style="font-weight: bold; color: #495057;">
                        {confidence_percentage}%
                    </div>
                </div>
            </div>

            {DataFormatter._format_key_insights(analysis.key_insights)}

            {DataFormatter._format_market_outlook(analysis.market_outlook)}
        </div>
        """

    @staticmethod
    def _format_key_insights(insights: List[str]) -> str:
        """Format key insights section."""
        if not insights:
            return ""

        insights_html = ""
        for insight in insights[:3]:  # Show top 3 insights
            insights_html += f"""
            <div style="
                background: rgba(76, 175, 80, 0.1);
                padding: 8px 12px;
                border-radius: 6px;
                margin: 4px 0;
                border-left: 3px solid #4caf50;
                font-size: 14px;
                color: #333;
            ">
                {UIConstants.ICONS['insights']} {insight}
            </div>
            """

        return f"""
        <div style="margin-top: 12px;">
            <div style="font-size: 14px; font-weight: bold; color: #495057; margin-bottom: 8px;">
                Key Insights
            </div>
            {insights_html}
        </div>
        """

    @staticmethod
    def _format_market_outlook(outlook: Optional[str]) -> str:
        """Format market outlook section."""
        if not outlook:
            return ""

        return f"""
        <div style="margin-top: 12px;">
            <div style="font-size: 14px; font-weight: bold; color: #495057; margin-bottom: 8px;">
                {UIConstants.ICONS['outlook']} Market Outlook
            </div>
            <div style="
                background: rgba(33, 150, 243, 0.1);
                padding: 8px 12px;
                border-radius: 6px;
                border-left: 3px solid #2196f3;
                font-size: 14px;
                color: #333;
                font-style: italic;
            ">
                {outlook}
            </div>
        </div>
        """

    @staticmethod
    def format_news_items(news_items: List[Dict[str, Any]]) -> str:
        """Format news items for display."""
        if not news_items:
            return ""

        news_html = ""
        for i, news in enumerate(news_items[:3], 1):  # Show top 3 news items
            headline = news.get("headline", "No headline")
            summary = news.get("summary", "No summary available")
            ticker = news.get("ticker", "N/A")
            source = news.get("source", "Unknown")

            news_html += f"""
            <div style="
                background: rgba(255, 152, 0, 0.1);
                padding: 12px;
                border-radius: 8px;
                margin: 8px 0;
                border-left: 3px solid #ff9800;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: bold; color: #333; font-size: 14px;">
                        {i}. {headline}
                    </span>
                    <span style="
                        background: #ff9800;
                        color: white;
                        padding: 2px 6px;
                        border-radius: 4px;
                        font-size: 12px;
                        font-weight: bold;
                    ">
                        {ticker}
                    </span>
                </div>
                <div style="color: #666; font-size: 13px; line-height: 1.4; margin-bottom: 4px;">
                    {summary}
                </div>
                <div style="font-size: 12px; color: #999; text-align: right;">
                    Source: {source}
                </div>
            </div>
            """

        return f"""
        <div style="margin-top: 16px;">
            <div style="font-size: 14px; font-weight: bold; color: #495057; margin-bottom: 8px;">
                {UIConstants.ICONS['news']} Related News
            </div>
            {news_html}
        </div>
        """

    @staticmethod
    def format_processing_status(message: str) -> str:
        """Format processing status message."""
        return f"""
        <div style="
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
            padding: 12px 16px;
            border-radius: 10px;
            margin: 8px 0;
            border-left: 4px solid #ff9800;
            display: flex;
            align-items: center;
            animation: pulse 2s infinite;
        ">
            <span style="font-size: 16px; margin-right: 10px; animation: spin 2s linear infinite;">
                {UIConstants.ICONS['loading']}
            </span>
            <span style="color: #e65100; font-weight: 500;">
                {message}
            </span>
        </div>

        <style>
            @keyframes pulse {{
                0% {{ opacity: 1; }}
                50% {{ opacity: 0.7; }}
                100% {{ opacity: 1; }}
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
        """

    @staticmethod
    def format_ticker_badges(tickers: List[str]) -> str:
        """Format ticker list as badges."""
        if not tickers:
            return ""

        badges_html = ""
        for ticker in tickers:
            badges_html += f"""
            <span style="
                background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
                margin: 2px;
                display: inline-block;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            ">
                {ticker}
            </span>
            """

        return badges_html

    @staticmethod
    def format_confidence_bar(confidence: float) -> str:
        """Format confidence score as a progress bar."""
        percentage = int(confidence * 100)

        # Color based on confidence level
        if confidence >= 0.8:
            color = UIConstants.SUCCESS_COLOR
        elif confidence >= 0.6:
            color = UIConstants.WARNING_COLOR
        else:
            color = UIConstants.ERROR_COLOR

        return f"""
        <div style="margin: 8px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="font-size: 12px; color: #666;">Confidence</span>
                <span style="font-size: 12px; font-weight: bold; color: {color};">{percentage}%</span>
            </div>
            <div style="
                background: #e0e0e0;
                height: 6px;
                border-radius: 3px;
                overflow: hidden;
            ">
                <div style="
                    background: {color};
                    height: 100%;
                    width: {percentage}%;
                    transition: width 0.3s ease;
                "></div>
            </div>
        </div>
        """
