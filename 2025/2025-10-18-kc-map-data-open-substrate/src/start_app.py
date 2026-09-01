#!/usr/bin/env python3
"""
Kansas City Data Platform - Startup Script

Single entry point for starting the application.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Start the Kansas City Data Platform application"""
    
    print("=" * 60)
    print("KANSAS CITY DATA PLATFORM")
    print("=" * 60)
    print()
    
    # Set environment variables
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('CONSOLIDATION_ENABLED', 'true')
    
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"Consolidation: {'Enabled' if os.environ.get('CONSOLIDATION_ENABLED', 'true').lower() == 'true' else 'Disabled'}")
    print()
    
    try:
        # Import and start the app
        from web.app import app
        app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: Failed to start application: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're in the project root directory")
        print("2. Check that all dependencies are installed: pip install -r requirements.txt")
        print("3. Verify the database file exists: data/processed/kc_data.gpkg")
        sys.exit(1)

if __name__ == '__main__':
    main()
