#!/usr/bin/env python3
"""
Debug Alfez Search
=================

Debug the specific Alfez search to see what's going wrong
"""

import sys
import os

# Add the scraper directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraper'))

from scraper.trolley_scraper import TrolleyScraper
from bs4 import BeautifulSoup
import urllib.parse

def debug_alfez_search():
    """Debug the Alfez search specifically"""
    print("🔍 DEBUGGING ALFEZ SEARCH")
    print("=" * 60)
    
    scraper = TrolleyScraper(browser_profile="chrome120")
    
    # Test the exact search term
    product_name = "Alfez Moroccan Cous Cous 200g"
    search_term = scraper._clean_search_term(product_name)
    
    print(f"Original product: {product_name}")
    print(f"Cleaned search term: {search_term}")
    print(f"Search URL: https://www.trolley.co.uk/search?q={search_term}")
    
    # Test brand extraction
    brand, product = scraper._extract_brand_and_product(product_name)
    print(f"Extracted brand: '{brand}'")
    print(f"Extracted product: '{product}'")
    
    # Test similarity with the wrong product that was found
    wrong_product = "Co-op Moroccan Cous Cous 215g"
    wrong_brand, wrong_product_name = scraper._extract_brand_and_product(wrong_product)
    print(f"\nWrong product: {wrong_product}")
    print(f"Wrong brand: '{wrong_brand}'")
    print(f"Wrong product name: '{wrong_product_name}'")
    
    similarity = scraper._calculate_similarity(product_name, wrong_product)
    print(f"Similarity score: {similarity:.3f}")
    
    # Test what the search actually returns
    print(f"\n🔍 Testing actual search...")
    results = scraper.search_product(product_name)
    
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"  Name: {result['name']}")
        print(f"  Brand: {result['brand']}")
        print(f"  URL: {result['url']}")
        print(f"  Similarity: {result['similarity_score']:.3f}")
        print(f"  Retailer prices: {list(result['retailer_prices'].keys())}")
        
        # Show detailed retailer prices
        for retailer, price_info in result['retailer_prices'].items():
            print(f"    {retailer}: £{price_info['price']}")

if __name__ == "__main__":
    debug_alfez_search()
