#!/usr/bin/env python3
"""
Video Generation API Server Startup Script
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from the root directory
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)

# Add the backend directory to Python path to ensure imports work
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Import and run the API server
from api_server import app

if __name__ == '__main__':
    print("🚀 Starting Video Generation API Server...")
    print("📍 Server will be available at: http://localhost:5001")
    print("🔍 Health check: http://localhost:5001/health")
    print("📋 API info: http://localhost:5001/")
    print("\n💡 Example usage:")
    print('curl -X POST http://localhost:5001/generate-video -H "Content-Type: application/json" -d \'{"topic": "lebron james and the lakers"}\'')
    print("\n" + "="*50)
    
    app.run(host='0.0.0.0', port=5001, debug=True) 