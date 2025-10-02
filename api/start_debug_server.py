#!/usr/bin/env python3
"""
Start FastAPI server with better error handling and logging
"""

import uvicorn
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def start_server():
    """Start the FastAPI server with debugging"""
    print("🚀 Starting FastAPI server with debugging...")
    
    try:
        # Import the app
        from main import app
        print("✅ Main app imported successfully")
        
        # Start server
        uvicorn.run(
            "main:app",
            host="127.0.0.1", 
            port=8000, 
            reload=True,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    start_server()