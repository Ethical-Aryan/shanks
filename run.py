"""
Root Launcher for Pirate Scrollytelling Web App
Run: python run.py
"""
import os
import sys

# Add backend directory to sys.path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

from app import app

if __name__ == '__main__':
    print("\n========================================================")
    print("  TIDES OF FORTUNE: Pirate Scrollytelling Experience")
    print("  Open in browser: http://127.0.0.1:5000")
    print("========================================================\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
