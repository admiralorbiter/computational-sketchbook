#!/usr/bin/env python3
"""
Alternative entry point for the Econ Explorer application.
This provides more configuration options and better error handling.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.factory import create_app

def main():
    """Main entry point with configuration."""
    try:
        app = create_app()
        
        # Configuration
        host = os.getenv("FLASK_HOST", "0.0.0.0")
        port = int(os.getenv("FLASK_PORT", "5000"))
        debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"
        
        print(f"Starting Econ Explorer on http://{host}:{port}")
        print(f"Debug mode: {debug}")
        print("Press Ctrl+C to stop the server")
        
        app.run(debug=debug, host=host, port=port)
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
