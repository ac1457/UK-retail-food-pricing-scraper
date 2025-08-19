#!/usr/bin/env python3
"""
Enhanced Scraper Test Script
============================

Test script for the enhanced scraper with curl_cffi bot detection avoidance.
This script demonstrates the enhanced functionality with browser impersonation.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.enhanced_custom_bulk_import import test_enhanced_excel_processing, enhanced_custom_bulk_import_products


def main():
    """Test the enhanced scraper functionality"""
    excel_file = "C:/Users/user/.cursor/Pricing Exp.xlsx"

    print("=" * 80)
    print("ENHANCED SCRAPER TEST WITH curl_cffi")
    print("=" * 80)
    print("This test demonstrates bot detection avoidance using curl_cffi")
    print("Available browser profiles: chrome120, firefox135, safari180, etc.")
    print("=" * 80)

    # Test 1: Enhanced Excel processing
    print("\n🧪 Test 1: Enhanced Excel Processing")
    print("-" * 50)
    
    browser_profiles = ["chrome120", "firefox135", "safari180"]
    
    for profile in browser_profiles:
        print(f"\nTesting with browser profile: {profile}")
        if test_enhanced_excel_processing(excel_file, browser_profile=profile):
            print(f"✅ Enhanced Excel processing PASSED with {profile}")
        else:
            print(f"❌ Enhanced Excel processing FAILED with {profile}")

    # Test 2: Enhanced search with different browser profiles
    print("\n\n🧪 Test 2: Enhanced Search Test")
    print("-" * 50)
    
    print("Testing enhanced search with Chrome 120 profile...")
    try:
        results = enhanced_custom_bulk_import_products(
            excel_file=excel_file,
            category="Test Category",
            min_score=0.3,
            max_products=2,  # Only test with 2 products
            auto_add=False,  # Don't add to scraper yet
            browser_profile="chrome120"
        )

        if results:
            print(f"✅ Enhanced search PASSED! Found {len(results)} results")
            print(f"Browser profiles used: {set(r.get('browser_profile', 'Unknown') for r in results)}")
        else:
            print("⚠️ Enhanced search completed but no results found")

    except Exception as e:
        print(f"❌ Enhanced search FAILED: {e}")

    # Test 3: Test with Firefox profile
    print("\nTesting enhanced search with Firefox 135 profile...")
    try:
        results = enhanced_custom_bulk_import_products(
            excel_file=excel_file,
            category="Test Category",
            min_score=0.3,
            max_products=1,  # Only test with 1 product
            auto_add=False,
            browser_profile="firefox135"
        )

        if results:
            print(f"✅ Firefox profile search PASSED! Found {len(results)} results")
        else:
            print("⚠️ Firefox profile search completed but no results found")

    except Exception as e:
        print(f"❌ Firefox profile search FAILED: {e}")

    print("\n" + "=" * 80)
    print("ENHANCED SCRAPER TESTING COMPLETED")
    print("=" * 80)
    print("\nTo use enhanced mode in production, run:")
    print("python main.py --custom-excel --enhanced --excel-file \"C:/Users/user/.cursor/Pricing Exp.xlsx\" --browser-profile chrome120 --max-products 10")
    print("\nAvailable browser profiles:")
    print("- chrome120, chrome119, chrome116")
    print("- firefox135, firefox133")
    print("- safari180, safari170")
    print("- edge99, edge101")


if __name__ == "__main__":
    main()
