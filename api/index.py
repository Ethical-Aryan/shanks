import os
import sys

# Add project root and backend to sys.path so modules and assets resolve correctly
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'backend'))

from backend.app import app

# Vercel serverless entrypoint
app = app
