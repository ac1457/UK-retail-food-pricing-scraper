#!/usr/bin/env python3
"""
Test Heinz Multipack Fix
=======================
Test the fix for Heinz Beanz 6 x 415g search issue
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.trolley_scraper_fixed import FixedTrolleyScraper


def test_heinz_fix():
    """Test the Heinz multipack fix"""
    print("🧪 Testing Heinz Multipack Fix")
    print("=" * 50)
    
    scraper = FixedTrolleyScraper()
    scraper.clear_cache()
    
    # Test the problematic product
    product_name = "Heinz Beanz 6 x 415g"
    
    print(f"🔍 Testing: {product_name}")
    print()
    
    # Test 1: Check if it's detected as multipack
    is_multipack = scraper._is_multipack(product_name)
    print(f"📦 Multipack detection: {is_multipack}")
    
    # Test 2: Check search term generation
    print(f"\n📝 Generated search terms:")
    search_terms = scraper._generate_search_terms(product_name)
    for i, term in enumerate(search_terms, 1):
        print(f"  {i}. {term}")
    
    # Test 3: Perform search
    print(f"\n🌐 Performing search...")
    results = scraper.search_product(product_name)
    
    if results:
        print(f"✅ Found {len(results)} results")
        
        # Show top 3 results
        for i, result in enumerate(results[:3], 1):
            print(f"\n  {i}. {result['name']}")
            print(f"     Similarity: {result['similarity_score']:.3f}")
            print(f"     URL: {result['url']}")
            
            if result.get('retailer_prices'):
                retailers = list(result['retailer_prices'].keys())
                print(f"     💰 Retailers: {retailers}")
                for retailer, price_info in result['retailer_prices'].items():
                    price = price_info.get('price', 'N/A')
                    print(f"        {retailer}: £{price}")
            else:
                print(f"     ❌ No prices found")
        
        # Check if we found the correct product
        best_match = max(results, key=lambda x: x['similarity_score'])
        correct_url = "https://www.trolley.co.uk/product/heinz-beanz-family-pack/DJC713"
        
        if correct_url in best_match['url']:
            print(f"\n🎉 SUCCESS: Found the correct product!")
            print(f"   URL: {best_match['url']}")
            if best_match.get('retailer_prices'):
                print(f"   ✅ Prices found: {list(best_match['retailer_prices'].keys())}")
            else:
                print(f"   ❌ No prices extracted")
        else:
            print(f"\n❌ Still matching wrong product")
            print(f"   Expected: {correct_url}")
            print(f"   Found: {best_match['url']}")
    else:
        print(f"❌ No search results found")
    
    print(f"\n🎯 Expected Result:")
    print(f"   Product: Heinz Baked Beans Family Pack")
    print(f"   Price: £4.74 (ASDA) or £5.00 (Tesco)")
    print(f"   URL: {correct_url}")


if __name__ == "__main__":
    test_heinz_fix()
