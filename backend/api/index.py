"""
Vercel Serverless Function entry point.
Routes all requests to the existing FastAPI ASGI app.
"""
import os
import sys

# Ensure the backend root directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app  # noqa: E402, F401
