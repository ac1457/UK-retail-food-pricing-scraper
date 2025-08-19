#!/usr/bin/env python3
"""
Test Fixed Search
================

Test the fixed search functionality
"""

import sys
import os

# Add the scraper directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraper'))

from scraper.trolley_scraper import TrolleyScraper

def test_fixed_search():
    """Test the fixed search functionality"""
    print("🔧 TESTING FIXED SEARCH")
    print("=" * 60)
    
    scraper = TrolleyScraper(browser_profile="chrome120")
    
    # Test the specific problematic case
    product_name = "Alfez Moroccan Cous Cous 200g"
    
    print(f"Searching for: {product_name}")
    print(f"Cleaned search term: {scraper._clean_search_term(product_name)}")
    
    # Test brand extraction
    brand, product = scraper._extract_brand_and_product(product_name)
    print(f"Brand: '{brand}'")
    print(f"Product: '{product}'")
    
    # Test similarity with wrong product
    wrong_product = "Co-op Moroccan Cous Cous 215g"
    similarity = scraper._calculate_similarity(product_name, wrong_product)
    print(f"Similarity with wrong product: {similarity:.3f}")
    
    # Test actual search
    print(f"\n🔍 Running search...")
    results = scraper.search_product(product_name)
    
    if results:
        print(f"\n✅ Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"  Name: {result['name']}")
            print(f"  Brand: {result['brand']}")
            print(f"  Similarity: {result['similarity_score']:.3f}")
            print(f"  URL: {result['url']}")
            
            if result['retailer_prices']:
                print(f"  Retailer prices:")
                for retailer, price_info in result['retailer_prices'].items():
                    print(f"    {retailer}: £{price_info['price']}")
            else:
                print(f"  No retailer prices found")
    else:
        print(f"\n❌ No results found - this might be correct if the product doesn't exist")

if __name__ == "__main__":
    test_fixed_search()
