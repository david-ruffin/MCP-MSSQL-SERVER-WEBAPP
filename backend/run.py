#!/usr/bin/env python3
import sys
import os

# Add the parent directory to the path so we can import the app package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api import start_server

if __name__ == "__main__":
    print("Starting SQL Chat API server...")
    start_server() 