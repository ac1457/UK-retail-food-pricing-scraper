#!/usr/bin/env python3
"""
Quick Test for Enhanced Scraper Fix
===================================

This script tests the enhanced scraper with the fixed key names.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.enhanced_custom_bulk_import import test_enhanced_excel_processing


def main():
    """Test the enhanced scraper fix"""
    excel_file = "C:/Users/user/.cursor/Pricing Exp.xlsx"
    
    print("🧪 TESTING ENHANCED SCRAPER FIX")
    print("=" * 50)
    
    # Test with Chrome profile
    print("\nTesting with Chrome 120 profile...")
    if test_enhanced_excel_processing(excel_file, browser_profile="chrome120"):
        print("✅ Enhanced Excel processing PASSED!")
    else:
        print("❌ Enhanced Excel processing FAILED!")
    
    print("\n" + "=" * 50)
    print("TEST COMPLETED")
    print("=" * 50)


if __name__ == "__main__":
    main()
