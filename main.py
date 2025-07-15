"""
Main entry point for the SharePoint AI Assistant.
Enhanced version with comprehensive error handling and logging.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from src.core import get_logger, setup_logging
    from src.ui import main as ui_main
    
    # Setup logging
    setup_logging()
    logger = get_logger("main")
    
    def main():
        """Main application entry point."""
        try:
            logger.info("Starting SharePoint AI Assistant (Enhanced Version)")
            logger.info(f"Python version: {sys.version}")
            logger.info(f"Working directory: {os.getcwd()}")
            
            # Run the Streamlit UI
            ui_main()
            
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
            sys.exit(0)
        except Exception as e:
            logger.critical(f"Critical error in main application: {e}")
            logger.critical(f"Exception type: {type(e).__name__}")
            import traceback
            logger.critical(f"Traceback: {traceback.format_exc()}")
            sys.exit(1)
    
    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install -r requirements/base.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Critical Error: {e}")
    print("Failed to start the application")
    sys.exit(1)
