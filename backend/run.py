#!/usr/bin/env python
"""
Run script for the Cloud Pilot application.

This script is a simple wrapper around the main function in src.main.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check if the OpenAI API key is set
if not os.environ.get("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY environment variable is not set.")
    print("Please create a .env file with your OpenAI API key or set it in your environment.")
    sys.exit(1)

# Import and run the main function
from src.main import main

if __name__ == "__main__":
    main()