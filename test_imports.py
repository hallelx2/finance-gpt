#!/usr/bin/env python3
"""
Test script to verify all imports work correctly.
Run this before starting the Streamlit app to catch import issues early.
"""

import sys
from pathlib import Path

# Add the project root and frontend to Python path
project_root = Path(__file__).parent
frontend_dir = project_root / "frontend"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(frontend_dir))


def test_imports():
    """Test all critical imports."""
    print("Testing imports...")

    try:
        print("✓ Testing core.config...")
        from core.config import AppConfig, UIConfig, UIConstants, SampleData, config

        print("✓ Testing core.state_manager...")
        from core.state_manager import StateManager, ChatMessage, AnalysisResult

        print("✓ Testing utils.formatters...")
        from utils.formatters import MessageFormatter, DataFormatter

        print("✓ Testing utils.ui_helpers...")
        from utils.ui_helpers import UIHelpers

        print("✓ Testing utils.validators...")
        from utils.validators import InputValidator

        print("✓ Testing components.ui_components...")
        from components.ui_components import (
            MessageComponent,
            StatusComponent,
            AnalysisComponent,
            InputComponent,
            SidebarComponent,
            MetricsComponent,
        )

        print("✓ Testing components.chat_interface...")
        from components.chat_interface import ChatInterface

        print("\n🎉 All imports successful!")
        return True

    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality of key components."""
    print("\nTesting basic functionality...")

    try:
        # Test StateManager
        from core.state_manager import StateManager

        state_manager = StateManager()
        print("✓ StateManager instantiation works")

        # Test AppConfig
        from core.config import AppConfig

        print(f"✓ App name: {AppConfig.APP_NAME}")
        print(f"✓ Version: {AppConfig.APP_VERSION}")

        # Test InputValidator
        from utils.validators import InputValidator

        is_valid, error = InputValidator.validate_query("Test query")
        print(f"✓ InputValidator works: {is_valid}")

        print("\n🎉 Basic functionality tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Functionality test error: {e}")
        return False


def main():
    """Main test function."""
    print("Finance GPT Frontend Import Test")
    print("=" * 40)

    # Test imports
    imports_ok = test_imports()

    if imports_ok:
        # Test basic functionality
        functionality_ok = test_basic_functionality()

        if functionality_ok:
            print("\n✅ All tests passed! You can now run the Streamlit app:")
            print("streamlit run frontend/main.py")
            return 0
        else:
            print("\n❌ Functionality tests failed!")
            return 1
    else:
        print("\n❌ Import tests failed!")
        return 1


if __name__ == "__main__":
    exit(main())
