#!/usr/bin/env python3
"""
Debug Price Extraction
=====================

Debug the price extraction from a specific product URL
"""

import sys
import os

# Add the scraper directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scraper'))

from scraper.trolley_scraper import TrolleyScraper
from bs4 import BeautifulSoup

def debug_price_extraction():
    """Debug price extraction from a specific URL"""
    print("🔍 DEBUGGING PRICE EXTRACTION")
    print("=" * 60)
    
    scraper = TrolleyScraper(browser_profile="chrome120")
    
    # Test with the specific URL that had wrong prices
    test_url = "https://www.trolley.co.uk/product/co-op-moroccan-style-cous-cous/RKT705"
    
    print(f"Testing URL: {test_url}")
    
    # Get the page content
    try:
        headers = scraper.session.headers.copy()
        headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        response = scraper.session.get(test_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Test the price extraction
            retailer_prices = scraper._parse_retailer_prices(soup)
            
            print(f"\nExtracted prices:")
            for retailer, price_info in retailer_prices.items():
                print(f"  {retailer}: £{price_info['price']}")
            
            # Also show the page text to see what's actually there
            print(f"\nPage text (first 1000 chars):")
            page_text = soup.get_text()[:1000]
            print(page_text)
            
        else:
            print(f"Failed to get page: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_price_extraction()
