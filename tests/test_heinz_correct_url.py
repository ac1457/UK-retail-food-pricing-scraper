#!/usr/bin/env python3
"""
Test script to debug Heinz multipack matching with correct URL
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scraper'))

from scraper.trolley_scraper_fixed import FixedTrolleyScraper

def test_heinz_correct_url():
    """Test the correct Heinz URL directly"""
    print("🧪 Testing Heinz multipack with correct URL")
    print("=" * 60)
    
    # Initialize scraper
    scraper = FixedTrolleyScraper()
    scraper.clear_cache()
    
    # The correct URL provided by user
    correct_url = "https://www.trolley.co.uk/product/heinz-beanz-family-pack/DJC713"
    
    print(f"🔗 Testing direct URL access: {correct_url}")
    
    try:
        # Test direct URL access
        prices = scraper._get_retailer_prices_fixed(correct_url)
        print(f"✅ Direct URL prices: {prices}")
        
        # Test search for "Heinz Beanz 6 x 415g"
        print(f"\n🔍 Testing search for: Heinz Beanz 6 x 415g")
        results = scraper.search_product("Heinz Beanz 6 x 415g")
        
        print(f"\n📊 Search Results ({len(results)} found):")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['name']}")
            print(f"   URL: {result['url']}")
            print(f"   Similarity: {result['similarity_score']:.3f}")
            print(f"   Prices: {result['retailer_prices']}")
            
            # Check if this is the correct product
            if "heinz-beanz-family-pack" in result['url']:
                print(f"   ✅ CORRECT PRODUCT FOUND!")
            else:
                print(f"   ❌ Wrong product")
        
        # Check if correct URL was found
        correct_found = any("heinz-beanz-family-pack" in result['url'] for result in results)
        
        if correct_found:
            print(f"\n🎉 SUCCESS: Correct Heinz Family Pack found!")
        else:
            print(f"\n❌ FAILURE: Correct Heinz Family Pack NOT found")
            print(f"Expected URL: {correct_url}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_heinz_correct_url()
