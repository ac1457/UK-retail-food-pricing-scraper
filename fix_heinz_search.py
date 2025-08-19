#!/usr/bin/env python3
"""
Fix Heinz Multipack Search Issue
===============================
Fix the search issue where Heinz Beanz 6 x 415g matches wrong products
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.trolley_scraper_fixed import FixedTrolleyScraper


def fix_heinz_search():
    """Fix the Heinz multipack search issue"""
    print("🔧 Fixing Heinz Multipack Search Issue")
    print("=" * 60)
    
    scraper = FixedTrolleyScraper(clear_cache=True)
    
    # The problematic search
    product_name = "Heinz Beanz 6 x 415g"
    
    print(f"🔍 Testing: {product_name}")
    print()
    
    # Test current search terms
    print("📝 Current Search Terms:")
    current_terms = scraper._generate_search_terms(product_name)
    for i, term in enumerate(current_terms, 1):
        print(f"  {i}. {term}")
    print()
    
    # Test with improved search terms
    print("🔄 Testing Improved Search Terms:")
    improved_terms = [
        "Heinz Beanz Family Pack",  # The actual product name on Trolley
        "Heinz Baked Beans 6 x 415g",
        "Heinz Beanz 6 pack",
        "Heinz Family Pack",
        "Heinz Beanz multipack"
    ]
    
    for term in improved_terms:
        print(f"\n🔍 Testing: '{term}'")
        results = scraper.search_product(term)
        
        if results:
            best_match = max(results, key=lambda x: x['similarity_score'])
            print(f"  ✅ Found: {best_match['name']}")
            print(f"     Similarity: {best_match['similarity_score']:.3f}")
            print(f"     URL: {best_match['url']}")
            
            if best_match.get('retailer_prices'):
                retailers = list(best_match['retailer_prices'].keys())
                print(f"     💰 Retailers: {retailers}")
                for retailer, price_info in best_match['retailer_prices'].items():
                    price = price_info.get('price', 'N/A')
                    print(f"        {retailer}: £{price}")
            else:
                print(f"     ❌ No prices found")
        else:
            print(f"  ❌ No results found")
    
    # Test the specific URL that should work
    print(f"\n🌐 Testing Direct URL Access:")
    correct_url = "https://www.trolley.co.uk/product/heinz-beanz-family-pack/DJC713"
    
    try:
        prices = scraper._get_retailer_prices_fixed(correct_url)
        if prices:
            print(f"  ✅ Direct URL works!")
            for retailer, price_info in prices.items():
                price = price_info.get('price', 'N/A')
                print(f"     {retailer}: £{price}")
        else:
            print(f"  ❌ Direct URL failed - no prices extracted")
    except Exception as e:
        print(f"  ❌ Direct URL failed: {e}")


def improve_search_terms():
    """Show how to improve search term generation"""
    print("\n💡 Search Term Improvements:")
    print("=" * 40)
    
    original = "Heinz Beanz 6 x 415g"
    
    # Current approach
    print(f"Original: {original}")
    print(f"Current terms would be: Heinz Beanz 6 x 415g, Heinz Beanz, Heinz")
    
    # Improved approach
    print(f"\nImproved terms should be:")
    print(f"1. Heinz Beanz Family Pack (exact product name)")
    print(f"2. Heinz Baked Beans 6 x 415g (full description)")
    print(f"3. Heinz Beanz 6 pack (simplified)")
    print(f"4. Heinz Family Pack (brand + pack type)")
    print(f"5. Heinz Beanz multipack (alternative term)")
    
    print(f"\n🎯 The key is to include 'Family Pack' in the search terms")


if __name__ == "__main__":
    fix_heinz_search()
    improve_search_terms()
