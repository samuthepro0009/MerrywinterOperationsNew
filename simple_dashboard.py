#!/usr/bin/env python3
"""
Simple dashboard script for Web Dashboard workflow
"""

import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the simple web server
from simple_web_server import main

if __name__ == "__main__":
    print("Starting FROST AI Web Dashboard...")
    main()