#!/usr/bin/env python3
"""
Quick Price Test
===============
Quick test to check if price extraction is working
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.trolley_scraper_fixed import FixedTrolleyScraper


def quick_price_test():
    """Quick test of price extraction"""
    print("⚡ Quick Price Extraction Test")
    print("=" * 50)
    
    scraper = FixedTrolleyScraper(clear_cache=True)
    
    # Test products
    test_products = [
        "Heinz Beanz 6 x 415g",  # The problematic one
        "Heinz Beanz 415g",      # Single version
        "Alfez Moroccan Cous Cous 200g",  # Known working product
        "Coca Cola 330ml",       # Simple product
    ]
    
    for product in test_products:
        print(f"\n🔍 Testing: {product}")
        print("-" * 40)
        
        results = scraper.search_product(product)
        
        if results:
            best_match = max(results, key=lambda x: x['similarity_score'])
            print(f"✅ Found: {best_match['name']}")
            print(f"   Similarity: {best_match['similarity_score']:.3f}")
            print(f"   URL: {best_match['url'][:60]}...")
            
            if best_match.get('retailer_prices'):
                retailers = list(best_match['retailer_prices'].keys())
                print(f"   💰 Retailers: {retailers}")
                
                # Show prices
                for retailer, price_info in best_match['retailer_prices'].items():
                    price = price_info.get('price', 'N/A')
                    print(f"      {retailer}: £{price}")
            else:
                print(f"   ❌ No retailer prices found")
        else:
            print(f"❌ No search results found")
    
    print(f"\n🎯 Quick Analysis:")
    print(f"  - If Alfez works but Heinz doesn't: Heinz product issue")
    print(f"  - If no products work: Price extraction broken")
    print(f"  - If single works but multipack doesn't: Multipack issue")


if __name__ == "__main__":
    quick_price_test()
