#!/usr/bin/env python3
"""
Setup script for MedEx Scraper
==============================

This script sets up the Scrapy + Playwright environment and installs all dependencies.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def main():
    print("🚀 MEDEX SCRAPER SETUP")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("pyproject_scraper.toml").exists():
        print("❌ pyproject_scraper.toml not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Rename pyproject_scraper.toml to pyproject.toml for installation
    if Path("pyproject_scraper.toml").exists() and not Path("pyproject.toml").exists():
        os.rename("pyproject_scraper.toml", "pyproject.toml")
        print("✅ Renamed pyproject_scraper.toml to pyproject.toml")
    
    # Install Python dependencies using uv
    if not run_command("uv sync", "Installing Python dependencies"):
        print("❌ Failed to install Python dependencies")
        return False
    
    # Install Playwright browsers
    if not run_command("uv run playwright install chromium", "Installing Playwright browsers"):
        print("❌ Failed to install Playwright browsers")
        return False
    
    print("\n🎉 SETUP COMPLETE!")
    print("=" * 50)
    print("Your Scrapy + Playwright scraper is ready!")
    print()
    print("To run the scraper:")
    print("  uv run scrapy crawl medex")
    print()
    print("To run with custom settings:")
    print("  uv run scrapy crawl medex -s DOWNLOAD_DELAY=5")
    print()
    print("Output files will be saved in:")
    print("  • scraped_data/medicines_TIMESTAMP.json")
    print("  • scraped_data/medicines_summary_TIMESTAMP.csv")
    

if __name__ == "__main__":
    main()
