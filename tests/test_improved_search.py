#!/usr/bin/env python3
"""
Test Improved Search Functionality
=================================

This script tests the improved search with multiple strategies, quantity extraction, and lower thresholds.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.enhanced_custom_bulk_import import enhanced_custom_bulk_import_products


def main():
    """Test the improved search functionality"""
    excel_file = "C:/Users/user/.cursor/Pricing Exp.xlsx"
    
    print("🧪 TESTING IMPROVED SEARCH FUNCTIONALITY")
    print("=" * 60)
    print("Testing with:")
    print("- Multiple search strategies")
    print("- Quantity extraction")
    print("- Lower similarity threshold (0.2)")
    print("- Brand and product separation")
    print("=" * 60)
    
    # Test with a small number of products
    try:
        results = enhanced_custom_bulk_import_products(
            excel_file=excel_file,
            category="Test Category",
            min_score=0.2,  # Lower threshold
            max_products=3,  # Test with 3 products
            auto_add=False,
            browser_profile="chrome120"
        )
        
        if results:
            print(f"\n✅ IMPROVED SEARCH SUCCESSFUL!")
            print(f"Found {len(results)} results")
            
            # Show some details about the results
            for i, result in enumerate(results[:3]):  # Show first 3 results
                print(f"\nResult {i+1}:")
                print(f"  Product: {result.get('name', 'N/A')}")
                print(f"  Website: {result.get('website', 'N/A')}")
                print(f"  Price: £{result.get('price', 0):.2f}")
                print(f"  Match Score: {result.get('match_score', 0):.2f}")
                print(f"  Original Quantity: {result.get('original_quantity', 'N/A')}")
                print(f"  Found Quantity: {result.get('found_quantity', 'N/A')}")
                print(f"  Search Strategy: {result.get('search_strategy', 'N/A')}")
        else:
            print("\n⚠️ No results found, but search completed without errors")
            
    except Exception as e:
        print(f"\n❌ SEARCH FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
